package angrycustomer.amass;

import angrycustomer.BaseToolTrain;
import angrycustomer.QuizzResolver;
import org.junit.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.Wait;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Instant;

import static angrycustomer.Randomizer.*;

public class BypassCaptcha extends BaseToolTrain {

    private QuizzResolver quizzResolver;

    public BypassCaptcha(int runIndex) {
        super(runIndex);

        quizzResolver = new QuizzResolver();
    }

    @Test
    public void testBypassContact() throws Exception {
        Instant startTime = Instant.now();

        driver.get("https://www.amass.ro/contact_amass.html");
        WebElement firstName = driver.findElement(By.id("nume"));
        firstName.sendKeys(randomNameGenerator());

        ((JavascriptExecutor) driver).executeScript("document.getElementById('ip').value = '" + randomIp() + "';");
        WebElement ip = driver.findElement(By.id("ip"));
        System.out.print(ip.getText());

        WebElement lastName = driver.findElement(By.id("prenume"));
        lastName.sendKeys(randomNameGenerator());

        WebElement oras = driver.findElement(By.id("oras"));
        oras.sendKeys(randomNameGenerator());

        WebElement telephone = driver.findElement(By.id("telefon"));
        telephone.sendKeys(randomNumber());

        WebElement email = driver.findElement(By.id("email"));
        email.sendKeys(randomNameGenerator() + "@hi5.ro");

        WebElement message = driver.findElement(By.id("mesaj"));
        message.sendKeys("#ciaoless");

        Wait<WebDriver> wait = new WebDriverWait(driver, 5000);

        Thread.sleep(4000);

        WebElement submit = driver.findElement(By.id("send-message"));
        wait.until(ExpectedConditions.elementToBeClickable(submit));
        submit.click();

        wait.until(driver1 -> String
                .valueOf(((JavascriptExecutor) driver1).executeScript("return document.readyState"))
                .equals("complete"));
        wait.until(driver1 -> driver1.findElement(By.cssSelector(".g-recaptcha")));

        WebElement submitMessage = driver.findElement(By.xpath("//*[@id=\"solutii_preview\"]/div[2]"));
        String textMessage = submitMessage.getText();

        Instant endTime = Instant.now();

        String out = "(took: " + getTimeDifference(startTime, endTime) + ") " + runIndex + ": " + textMessage;
        if (textMessage != null && textMessage.contains("trimis")) {
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

        WebElement quiz = driver.findElement(By.cssSelector(".wpcf7-quiz"));
        String question = driver.findElement(By.cssSelector(".wpcf7-quiz-label")).getText();
        quiz.sendKeys(quizzResolver.solveQuizCalculation(question));

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
}
