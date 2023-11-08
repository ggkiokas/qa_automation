from functools import wraps
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class BrowserUtils:
    @staticmethod
    def open_new_tab(driver, url_to_open):
        driver.execute_script(f'window.open("{url_to_open}", "_blank");')

    @staticmethod
    def navigate_to_url(driver, url):
        driver.get(url)

    @staticmethod
    def refresh_page(driver):
        driver.refresh()

    @staticmethod
    def switch_to_tab_and_back_to_current(target_tab_index, should_switch_back=True):
        def decorator(func):
            @wraps(func)
            def wrapper(context, *args, **kwargs):
                current_tab = context.driver.current_window_handle
                all_tabs = context.driver.window_handles
                context.driver.switch_to.window(all_tabs[target_tab_index])
                result = func(context, *args, **kwargs)
                if should_switch_back is True:
                    context.driver.switch_to.window(current_tab)
                return result

            return wrapper

        return decorator
