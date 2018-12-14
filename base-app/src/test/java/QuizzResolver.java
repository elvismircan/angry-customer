import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class QuizzResolver {

    public String solveQuiz(String question) {
        String regex ="(\\d+)";
        Matcher matcher = Pattern.compile( regex ).matcher( question);

        List<Integer> numbers = new ArrayList<Integer>();

        while (matcher.find()) {
            numbers.add(Integer.valueOf(matcher.group()));
        }
        Collections.sort(numbers);

        return String.valueOf(numbers.get(0));
    }

    public String solveQuizCalculation(String question) throws ScriptException {
        question = question.replace("x", "*" );

        ScriptEngineManager script = new ScriptEngineManager();
        ScriptEngine engine = script.getEngineByName("JavaScript");
        return String.valueOf(engine.eval(question.substring(0, question.length() - 2)));
    }
}
