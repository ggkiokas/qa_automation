import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions

from common.constants import *
from frontend.selenium_wd.src.configs.setup_configs import SetUpConfigsForTest
from common.log_config import configure_logger

logger = configure_logger(__name__)


class BasePage:
    def __init__(self, custom_options=None):
        self.setup = SetUpConfigsForTest()
        self.machine = self.setup.machine
        self.browser = self.setup.browser
        self.download_dir = POSEIDON_DIR
        self.DEVICE_VIEW = self.setup.DEVICE_VIEW
        self.emulation = self.setup.emulation
        self.mapped_browsers = {
            CHROME: {
                "driver": webdriver.Chrome,
                "executable_path": ChromeDriverManager,
                "options": ChromeOptions,
                "version": "chrome",
            },
            FIREFOX: {
                "driver": webdriver.Firefox,
                "executable_path": GeckoDriverManager,
                "options": FirefoxOptions,
                "version": "moz:geckodriverVersion",
            },
            SAFARI: {
                "driver": webdriver.Safari,
                "executable_path": "",
                "options": SafariOptions,
                "version": "version",
            },
        }
        self.custom_options = custom_options

    def launch_selected_browser(self):
        webdriver_exec = self.get_webdriver_exec()
        options = self.set_general_options_to_browser()
        self.driver = self.mapped_browsers[self.browser]["driver"](
            executable_path=webdriver_exec, options=options
        )  # you can set your custom executable_path here or your custom options. If not default will be used
        self.log_browser_version()

    def get_webdriver_exec(self):
        webdriver_exec = self.mapped_browsers[self.browser]["executable_path"]()
        if webdriver_exec:
            webdriver_exec = webdriver_exec.install()

        return webdriver_exec

    def set_general_options_to_browser(self):
        options = self.mapped_browsers[self.browser]["options"]()
        self.add_download_dir(options)
        options.add_argument("--start-maximized")
        options.add_argument("window-size=1920x1080")
        if os.environ.get("HD"):
            options.add_argument("--headless")
        # options.add_experimental_option('detach',False)
        self.set_custom_options_to_browser(options)

        return options

    def add_download_dir(self, options):
        preferences = {"download.default_directory": self.download_dir}
        options.add_experimental_option("prefs", preferences)

    def set_custom_options_to_browser(self, options):
        if self.DEVICE_VIEW == "mobile":
            options.add_experimental_option("mobileEmulation", self.emulation)

        if self.machine in ["docker", "github_actions"]:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # options.add_argument("--disable-gpu")
            # options.add_argument("--enable-logging")
            # options.add_argument("--v=1")

        if self.custom_options:
            if self.custom_options.get("disable_cookies") is True:
                self.disable_cookies(options)

    def log_browser_version(self):
        # Get the chromedriver version from the WebDriver
        version_mapping = self.mapped_browsers[self.browser]["version"]
        driver_version = self.driver.capabilities.get(version_mapping)
        if version_mapping == CHROME:
            driver_version = driver_version.get("chromedriverVersion")

        # Print the chromedriver version
        logger.debug(f"Driver Version: {driver_version}")

    def disable_cookies(self, options):
        if self.browser == CHROME:
            options.add_argument("--disable-cookies")
        elif self.browser == "firefox":
            options.set_preference("network.cookie.cookieBehavior", 2)
