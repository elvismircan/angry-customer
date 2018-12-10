import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.Wait;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.io.*;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.text.SimpleDateFormat;
import java.time.Duration;
import java.time.Instant;

import static org.junit.Assert.assertTrue;

public class BypassCaptcha {

    private WebDriver driver;

    @Before
    public void setUp() {

        ChromeOptions options = new ChromeOptions();
        options.addArguments("start-maximized");
        options.addArguments("--headless");
        options.addArguments("incognito");

        System.setProperty("webdriver.chrome.driver", "src/test/resources/chromedriver.exe");

        driver = new ChromeDriver(options);
    }

    @Test
    public void testReadCaptcha() throws IOException {
        String result = runCaptchaTool();
        System.out.println(result);
        assertTrue(!result.isEmpty());
    }

    @Test
    public void testBypass() throws Exception {
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

    private String getTimeDifference(Instant start, Instant end) {
        Duration timeElapsed = Duration.between(start, end);
        return timeElapsed.toMinutes() + ":" + timeElapsed.getSeconds();
    }

    private String readCaptcha() {
        WebElement img = driver.findElement(By.className("wpcf7-captcha-captcha-926"));
        String src = img.getAttribute("src");

        try(InputStream in = new URL(src).openStream()) {
            Path path = Paths.get("../base-tool/real_captcha_images/captcha.png");
            Files.copy(in, path, StandardCopyOption.REPLACE_EXISTING);

            String result = runCaptchaTool();
            return result;

        } catch (Exception e) {
            return null;
        }

    }

    private String runCaptchaTool() throws IOException {
        String toolDir = new File("..").getAbsolutePath() + File.separator + "base-tool";

        return executeCommand("cmd /c \"cd d: && cd " + toolDir + " && python solve_captchas_with_model.py\" ");
    }

    private String executeCommand(String command) {

        String result = "";

        try {
            Process p = Runtime.getRuntime().exec(command);
            p.waitFor();

            BufferedReader stdError = new BufferedReader(new InputStreamReader(p.getErrorStream()));
//            System.out.println(readStream(stdError));

            BufferedReader stdInput = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String output = readStream(stdInput);
            result = output.substring(output.lastIndexOf(":") + 2, output.length());

        } catch (Exception e) {
            e.printStackTrace();
        }

        return result.toString();
    }

    private String readStream(BufferedReader br) throws IOException {
        String lastLine = null;

        String line = br.readLine();
        while ( line != null) {
            lastLine = line;
            line = br.readLine();
        }

        return lastLine;
    }

    @After
    public void tearDown() throws Exception {
        driver.quit();
    }
}