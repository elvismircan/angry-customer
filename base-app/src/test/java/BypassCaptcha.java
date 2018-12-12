import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.Wait;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.time.Duration;
import java.time.Instant;

import static org.junit.Assert.assertTrue;

public class BypassCaptcha {

    private WebDriver driver;

    private CaptchaResolver captchaResolver;

    @Before
    public void setUp() {

        ChromeOptions options = new ChromeOptions();
        options.addArguments("start-maximized");
        options.addArguments("--headless");
        options.addArguments("incognito");

        System.setProperty("webdriver.chrome.driver", "src/test/resources/chromedriver.exe");

        driver = new ChromeDriver(options);
        captchaResolver = new CaptchaResolver();
    }

//    @Test
    public void testReadCaptcha() throws IOException {
        String result = captchaResolver.runCaptchaTool();
        System.out.println(result);
        assertTrue(!result.isEmpty());
    }

    @Test
    public void testBypassContact() throws Exception {
        SimpleDateFormat format = new SimpleDateFormat("yy/MM/dd HH:mm:ss");

        for (int i=1;;i++) {
            Instant startTime = Instant.now();

            driver.get("https://www.amass.ro/contact_amass.html");
            WebElement firstName = driver.findElement(By.name("text-458"));
            firstName.sendKeys("Les");

            WebElement lastName = driver.findElement(By.name("text-610"));
            lastName.sendKeys("Bulan");

            WebElement telephone = driver.findElement(By.name("tel-142"));
            telephone.sendKeys("0745001254");

            WebElement email = driver.findElement(By.name("email-624"));
            email.sendKeys("les.bulan@hi5.ro");

            WebElement message = driver.findElement(By.name("textarea-144"));
            message.sendKeys("#ciaoless");

            WebElement file = driver.findElement(By.name("file-784"));
//            file.sendKeys("d:\\Projects_Personal\\angry-customer\\base-app\\special.zip");

            WebElement accept = driver.findElement(By.name("acceptance-172"));
            ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView();", accept);
            accept.click();

            WebElement captcha = driver.findElement(By.name("captcha-926"));
            captcha.sendKeys(readCaptcha());

            WebElement submit = driver.findElement(By.cssSelector(".wpcf7-submit"));
            submit.click();

            Wait<WebDriver> wait = new WebDriverWait(driver, 5000);
            wait.until(driver1 -> String
                    .valueOf(((JavascriptExecutor) driver1).executeScript("return document.readyState"))
                    .equals("complete"));

            WebElement submitMessage = driver.findElement(By.cssSelector(".screen-reader-response"));
            submitMessage.isDisplayed();
            String textMessage = submitMessage.getText();

            Instant endTime = Instant.now();

            String out = "(took: " + getTimeDifference(startTime, endTime) + ") " + i + ": " + textMessage;
            if (textMessage != null && !textMessage.contains("erori")) {
                System.out.println("+ " + out);
            } else {
                System.out.println("- " + out);
            }
        }
    }

    @Test
    public void testBypassQuote() throws Exception {
        SimpleDateFormat format = new SimpleDateFormat("yy/MM/dd HH:mm:ss");

        for (int i=1;;i++) {
            Instant startTime = Instant.now();

            driver.get("https://www.amass.ro/cere-o-cotatie-pentru-incalzirea-electrica");
            Select domain = new Select(driver.findElement(By.name("domeniu")));
            domain.selectByVisibleText("Protectie inghet");

            WebElement firstName = driver.findElement(By.name("text-306"));
            firstName.sendKeys("Les");

            WebElement lastName = driver.findElement(By.name("text-128"));
            lastName.sendKeys("Bulan");

            WebElement telephone = driver.findElement(By.name("tel-91"));
            telephone.sendKeys("0745001254");

            WebElement email = driver.findElement(By.name("email-851"));
            email.sendKeys("les.bulan@hi5.ro");

            WebElement surface = driver.findElement(By.name("text-475"));
            surface.sendKeys("1000");

            Select destination = new Select(driver.findElement(By.name("destinatie")));
            destination.selectByVisibleText("magazine");

            Select floor = new Select(driver.findElement(By.name("pardoseala")));
            floor.selectByVisibleText("granit");

            Select heating = new Select(driver.findElement(By.name("incalzire")));
            heating.selectByVisibleText("incalzire totala");

            WebElement city = driver.findElement(By.name("text-799"));
            city.sendKeys("Vaslui");

            WebElement message = driver.findElement(By.name("textarea-218"));
            message.sendKeys("#blank");

            WebElement file = driver.findElement(By.name("file-784"));
//            file.sendKeys("d:\\Projects_Personal\\angry-customer\\base-app\\special.zip");

            WebElement accept = driver.findElement(By.name("acceptance-611"));
            ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView();", accept);
            accept.click();

            WebElement captcha = driver.findElement(By.name("captcha-926"));
            captcha.sendKeys(readCaptcha());

            WebElement submit = driver.findElement(By.cssSelector(".wpcf7-submit"));
            submit.click();

            Wait<WebDriver> wait = new WebDriverWait(driver, 5000);
            wait.until(driver1 -> String
                    .valueOf(((JavascriptExecutor) driver1).executeScript("return document.readyState"))
                    .equals("complete"));

            WebElement submitMessage = driver.findElement(By.cssSelector(".screen-reader-response"));
            submitMessage.isDisplayed();
            String textMessage = submitMessage.getText();

            Instant endTime = Instant.now();

            String out = "(took: " + getTimeDifference(startTime, endTime) + ") " + i + ": " + textMessage;
            if (textMessage != null && !textMessage.contains("erori")) {
                System.out.println("+ " + out);
            } else {
                System.out.println("- " + out);
            }
        }
    }

    private String getTimeDifference(Instant start, Instant end) {
        Duration timeElapsed = Duration.between(start, end);
        return timeElapsed.toMinutes() + ":" + timeElapsed.getSeconds();
    }

    private String readCaptcha() {
        WebElement img = driver.findElement(By.className("wpcf7-captcha-captcha-926"));
        String src = img.getAttribute("src");

        return captchaResolver.readCaptcha(src);
    }

    @After
    public void tearDown() throws Exception {
        driver.quit();
    }
}