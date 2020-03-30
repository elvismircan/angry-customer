package angrycustomer.acumconstruct;

import angrycustomer.BaseToolTrain;
import org.junit.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;

import java.time.Instant;

import static angrycustomer.Randomizer.randomNameGenerator;
import static angrycustomer.Randomizer.randomNumber;

public class BypassCaptcha extends BaseToolTrain {

    public BypassCaptcha(int runIndex) {
        super(runIndex);
    }

    @Test
    public void testBypassContact() throws Exception {
        Instant startTime = Instant.now();

        driver.get("http://www.acumconstruct.ro/incalzire-in-pardoseala-cerere-de-oferta");
        WebElement firstName = driver.findElement(By.name("nume"));
        firstName.sendKeys(randomNameGenerator());

        WebElement telephone = driver.findElement(By.name("telefon"));
        telephone.sendKeys(randomNumber());

        WebElement email = driver.findElement(By.name("email"));
        email.sendKeys(randomNameGenerator() + "@hi5.ro");

        WebElement message = driver.findElement(By.name("mesaj"));
        message.sendKeys("#ciaoless");

        WebElement captcha = driver.findElement(By.name("code"));
        captcha.sendKeys(readCaptcha("__code__", "captcha.png"));

        Instant endTime = Instant.now();

        String out = "(took: " + getTimeDifference(startTime, endTime) + ") " + runIndex;

        System.out.println("- " + out);
    }
}
