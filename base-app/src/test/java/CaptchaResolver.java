import java.io.*;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

public class CaptchaResolver {

    public String readCaptcha(String url) {
        try(InputStream in = new URL(url).openStream()) {
            Path path = Paths.get("../base-tool/real_captcha_images/captcha.png");
            Files.copy(in, path, StandardCopyOption.REPLACE_EXISTING);

            String result = runCaptchaTool();
            return result;

        } catch (Exception e) {
            return null;
        }

    }

    public String runCaptchaTool() throws IOException {
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
}
