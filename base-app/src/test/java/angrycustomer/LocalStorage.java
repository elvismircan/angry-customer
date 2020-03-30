package angrycustomer;

import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;

public class LocalStorage {
    private JavascriptExecutor js;

    public LocalStorage(WebDriver webDriver) {
        this.js = (JavascriptExecutor) webDriver;
    }

    public void removeItemFromLocalStorage(String item) {
        js.executeScript(String.format(
                "window.sessionStorage.removeItem('%s');", item));
    }

    public boolean isItemPresentInLocalStorage(String item) {
        return !(js.executeScript(String.format(
                "return window.sessionStorage.getItem('%s');", item)) == null);
    }

    public String getItemFromLocalStorage(String key) {
        return (String) js.executeScript(String.format(
                "return window.sessionStorage.getItem('%s');", key));
    }

    public String getKeyFromLocalStorage(int key) {
        return (String) js.executeScript(String.format(
                "return window.sessionStorage.key('%s');", key));
    }

    public Long getLocalStorageLength() {
        return (Long) js.executeScript("return window.sessionStorage.length;");
    }

    public void setItemInLocalStorage(String item, String value) {
        js.executeScript(String.format(
                "window.sessionStorage.setItem('%s','%s');", item, value));
    }

    public void clearLocalStorage() {
        js.executeScript(String.format("window.sessionStorage.clear();"));
    }
}
