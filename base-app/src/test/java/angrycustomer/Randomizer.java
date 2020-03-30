package angrycustomer;

import org.apache.commons.lang3.RandomStringUtils;

public class Randomizer {

    public static String randomNameGenerator() {
        return RandomStringUtils.random(7, true, false);
    }

    public static String randomNumber() {
        return "0745" + RandomStringUtils.randomNumeric(6);
    }

    public static String randomIp() {
        return RandomStringUtils.randomNumeric(3) + "." +
                RandomStringUtils.randomNumeric(3) + "." +
                RandomStringUtils.randomNumeric(3) + "." +
                RandomStringUtils.randomNumeric(3);
    }
}
