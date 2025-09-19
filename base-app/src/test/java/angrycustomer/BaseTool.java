package angrycustomer;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

@RunWith(Parameterized.class)
public class BaseTool {

    protected static WebDriver driver;
    protected int runIndex;

    public BaseTool(int runIndex) {
        this.runIndex = runIndex;
    }

    @Parameterized.Parameters
    public static Collection data() {
        int length = 1;
        List<Integer> index = new ArrayList<>();
        for (int i = 0; i < length; i++) {
            index.add(i);
        }

        return index;
    }

    @BeforeClass
    public static void setUp() {

        ChromeOptions options = new ChromeOptions();
        options.addArguments("start-maximized");
        options.addArguments("disable-infobars");
        options.addArguments("--headless");
        options.addArguments("--incognito");

//        System.setProperty("webdriver.chrome.driver", "src/test/resources/chromedriver.exe");
        System.setProperty("webdriver.chrome.driver", "/usr/local/bin/chromedriver");

        driver = new ChromeDriver(options);
        logExternalIPAddress();
    }

    @AfterClass
    public static void tearDown() {
        driver.quit();
    }

    @After
    public void after() throws InterruptedException {
        Thread.sleep(3000);
    }

    protected String getTimeDifference(Instant start, Instant end) {
        Duration timeElapsed = Duration.between(start, end);
        return timeElapsed.toMinutes() + ":" + timeElapsed.getSeconds();
    }

    protected static void logExternalIPAddress() {
        try {
            String urlString = "http://checkip.amazonaws.com/";
            URL url = new URL(urlString);
            try (BufferedReader br = new BufferedReader(new InputStreamReader(url.openStream()))) {
                System.out.println("External IP address is: " + br.readLine());
            }
        } catch (IOException e) {
            System.out.println("Failed to get machine IP address! " + e);
        }
    }
}
