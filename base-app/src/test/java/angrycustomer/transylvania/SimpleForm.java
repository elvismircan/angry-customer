package angrycustomer.transylvania;

import static angrycustomer.Randomizer.randomNameGenerator;
import angrycustomer.BaseTool;
import java.time.Instant;
import org.junit.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Wait;
import org.openqa.selenium.support.ui.WebDriverWait;

public class SimpleForm extends BaseTool {

    public SimpleForm(int runIndex) {
        super(runIndex);
    }

    @Test
    public void testBypassContact() throws Exception {
        Instant startTime = Instant.now();

        driver.get("https://bam-bam.ro/");
        WebElement firstName = driver.findElement(By.id("firstNameInput"));
        firstName.sendKeys(randomNameGenerator());

        WebElement lastName = driver.findElement(By.id("lastNameInput"));
        lastName.sendKeys(randomNameGenerator());

        WebElement email = driver.findElement(By.id("emailInput"));
        email.sendKeys(randomNameGenerator() + "@hi5.ro");

        WebElement message = driver.findElement(By.id("messageInput"));
        message.sendKeys("#ciaoless");

        Wait<WebDriver> wait = new WebDriverWait(driver, 5000);

        Thread.sleep(4000);

        WebElement submit = driver.findElement(By.id("submitInput"));
        wait.until(ExpectedConditions.elementToBeClickable(submit));
        System.out.println("Clicked submit!");
//        submit.click();

        Instant endTime = Instant.now();

        System.out.println("(took: " + getTimeDifference(startTime, endTime) + ") " + runIndex);
    }

}
