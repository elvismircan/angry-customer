import org.apache.commons.lang3.RandomStringUtils;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.Wait;
import org.openqa.selenium.support.ui.WebDriverWait;

import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.junit.Assert.assertTrue;

@RunWith(Parameterized.class)
public class BypassCaptcha {

    private int runIndex;

    private static WebDriver driver;

    private static CaptchaResolver captchaResolver;

    public BypassCaptcha(int runIndex) {
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
        Instant startTime = Instant.now();

        driver.get("https://www.amass.ro/contact_amass.html");
        WebElement firstName = driver.findElement(By.name("text-458"));
        firstName.sendKeys(randomNameGenerator());

        WebElement lastName = driver.findElement(By.name("text-610"));
        lastName.sendKeys(randomNameGenerator());

        WebElement telephone = driver.findElement(By.name("tel-142"));
        telephone.sendKeys(randomNumber());

        WebElement email = driver.findElement(By.name("email-624"));
        email.sendKeys(randomNameGenerator() + "@hi5.ro");

        WebElement message = driver.findElement(By.name("textarea-144"));
        message.sendKeys("#ciaoless");

        WebElement file = driver.findElement(By.name("file-784"));
//            file.sendKeys("d:\\Projects_Personal\\angry-customer\\base-app\\special.zip");

        WebElement accept = driver.findElement(By.name("acceptance-172"));
        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView();", accept);
        accept.click();

        WebElement quiz = driver.findElement(By.cssSelector(".wpcf7-quiz"));
        quiz.sendKeys(solveQuizCalculation());

//        WebElement captcha = driver.findElement(By.name("captcha-926"));
//        captcha.sendKeys(readCaptcha());

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

        String out = "(took: " + getTimeDifference(startTime, endTime) + ") " + runIndex + ": " + textMessage;
        if (textMessage != null && !textMessage.contains("erori")) {
            System.out.println("+ " + out);
        } else {
            System.out.println("- " + out);
        }
    }

    @Test
    public void testBypassQuote() throws Exception {
        Instant startTime = Instant.now();

        driver.get("https://www.amass.ro/cere-o-cotatie-pentru-incalzirea-electrica");
        Select domain = new Select(driver.findElement(By.name("domeniu")));
        domain.selectByVisibleText("Protectie inghet");

        WebElement firstName = driver.findElement(By.name("text-306"));
        firstName.sendKeys(randomNameGenerator());

        WebElement lastName = driver.findElement(By.name("text-128"));
        lastName.sendKeys(randomNameGenerator());

        WebElement telephone = driver.findElement(By.name("tel-91"));
        telephone.sendKeys(randomNumber());

        WebElement email = driver.findElement(By.name("email-851"));
        email.sendKeys(randomNameGenerator() + "@hi5.ro");

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

        WebElement quiz = driver.findElement(By.cssSelector(".wpcf7-quiz"));
        quiz.sendKeys(solveQuizCalculation());

//            WebElement captcha = driver.findElement(By.name("captcha-926"));
//            captcha.sendKeys(readCaptcha());

        WebElement accept = driver.findElement(By.name("acceptance-611"));
        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView();", accept);
        accept.click();

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

        String out = "(took: " + getTimeDifference(startTime, endTime) + ") " + runIndex + ": " + textMessage;
        if (textMessage != null && !textMessage.contains("erori")) {
            System.out.println("+ " + out);
        } else {
            System.out.println("- " + out);
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


    public String randomNameGenerator() {
        return RandomStringUtils.random(7, true, false);
    }

    public String randomNumber() {
        return "0745" + RandomStringUtils.randomNumeric(6);
    }

    public String solveQuiz() {
        String question = driver.findElement(By.cssSelector(".wpcf7-quiz-label")).getText();

        String regex ="(\\d+)";
        Matcher matcher = Pattern.compile( regex ).matcher( question);

        List<Integer> numbers = new ArrayList<Integer>();

        while (matcher.find()) {
            numbers.add(Integer.valueOf(matcher.group()));
        }
        Collections.sort(numbers);

        return String.valueOf(numbers.get(0));
    }

    public String solveQuizCalculation() throws ScriptException {
        String question = driver.findElement(By.cssSelector(".wpcf7-quiz-label")).getText();
        question = question.replace("x", "*" );

        System.out.println(question);

        ScriptEngineManager script = new ScriptEngineManager();
        ScriptEngine engine = script.getEngineByName("JavaScript");
        return String.valueOf(engine.eval(question.substring(0, question.length() - 2)));
    }

    @AfterClass
    public static void tearDown() throws Exception {
        driver.quit();
    }
}