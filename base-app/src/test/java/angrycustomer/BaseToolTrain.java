package angrycustomer;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import java.io.File;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.junit.Assert.assertTrue;

@RunWith(Parameterized.class)
public class BaseToolTrain {

    protected int runIndex;

    protected static WebDriver driver;

    protected static CaptchaResolver captchaResolver;

    public BaseToolTrain(int runIndex) {
        this.runIndex = runIndex;
    }

    @Parameterized.Parameters
    public static Collection data() {
        int length = 1000;
        List<Integer> index = new ArrayList<>();
        for(int i = 0; i < length; i++ ) {
            index.add(i);
        }

        return index;
    }

    @BeforeClass
    public static void setUp() {

        ChromeOptions options = new ChromeOptions();
        options.addArguments("start-maximized");
        options.addArguments("disable-infobars");
//        options.addArguments("--headless");
        options.addArguments("incognito");
        options.addExtensions(new File("src/test/resources/captcha-clicker.crx"));

        System.setProperty("webdriver.chrome.driver", "src/test/resources/chromedriver.exe");

        driver = new ChromeDriver(options);
        captchaResolver = new CaptchaResolver();
    }

    @AfterClass
    public static void tearDown() throws Exception {
        driver.quit();
    }

    @After
    public void after() throws InterruptedException {
        Thread.sleep(3000);
    }

    @Test
    public void getImagesToTrainModel() throws Exception {
        driver.get("http://www.acumconstruct.ro/incalzire-in-pardoseala-cerere-de-oferta");
        downloadCaptchaImage("__code__", "captcha" + runIndex + ".png");
    }

    @Test
    public void testReadCaptcha() throws IOException {
        String result = captchaResolver.runCaptchaTool();
        System.out.println(result);
        assertTrue(!result.isEmpty());
    }

    private String getImageSrc(String element) {
        WebElement img = driver.findElement(By.id(element));
        return img.getAttribute("src");
    }

    protected String readCaptcha(String element, String fileName) {
        String src = getImageSrc(element);
        return captchaResolver.readCaptcha(src, fileName);
    }

    protected void downloadCaptchaImage(String element, String fileName) {
        String src = getImageSrc(element);
        captchaResolver.downloadCaptcha(src, fileName);
    }

    protected String getTimeDifference(Instant start, Instant end) {
        Duration timeElapsed = Duration.between(start, end);
        return timeElapsed.toMinutes() + ":" + timeElapsed.getSeconds();
    }
}
