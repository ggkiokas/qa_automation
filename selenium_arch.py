from collections import namedtuple
import traceback,sys,time,os,glob,json
from pathlib import Path
from email.mime.text import MIMEText
import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

class BasePage:
    def __init__(self,driver):
        self.driver = driver
    
    def GoTo(self,url):
        self.driver.get(url)

class BaseElement:

    def __init__(self,driver,locator,timeout):
        self.driver = driver
        self.locator = locator
        self.timeout = timeout
        self.web_element = None
        self.Find()

    def Find(self):
        self.web_element = WebDriverWait(self.driver, self.timeout).\
                            until(EC.visibility_of_element_located(locator=self.locator))
        print(self.web_element.text)

    def Click(self):
        element = WebDriverWait(self.driver,self.timeout).\
                    until(EC.element_to_be_clickable(locator= self.locator))
    
    def Clear(self):
        self.web_element.clear()

    def ClearManually(self,iter_num):
        for i in range(iter_num):
            self.web_element.send_keys(Keys.BACK_SPACE)
            self.web_element.send_keys(Keys.BACK_SPACE)
            self.web_element.send_keys(Keys.CONTROL + "a")
            self.web_element.send_keys(Keys.DELETE)

    def attribute(self,attr_name):
        attribute = self.web_element.get_attribute(attr_name)
        return attribute
    
    def Enter(self):
        self.web_element.send_keys(Keys.ENTER)

    @property
    def text(self):
        return self.web_element.text
    
    @text.setter
    def text(self,value):
        self.web_element.send_keys(value)

Locator = namedtuple('Locator',['by','value'])

class BaseElementDescriptor:

    def __init__(self,locator, timeout=1):
        self.locator = locator
        self.timeout = timeout
    
    def __get__(self,instance,owner_class):
        return BaseElement(driver=instance.driver, locator= self.locator, timeout=self.timeout)

class GooglePage(BasePage):
    search_textbox = BaseElementDescriptor(Locator(by=By.XPATH,\
                                                   value ="//input[@name='q']/../input"))

    cookies_btns = BaseElementDescriptor(Locator(by=By.XPATH,\
                                                   value ="//div[contains(@class,'QS5gu sy4vM')]"))

    def __init__(self,driver):
        super().__init__(driver)

class DummyTestCase:

    def __init__(self):
        self.google_url = 'https://www.google.com/'

    def LoadDrivers(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_experimental_option('detach',False)
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)
    
    def NewGoogleSearch(self):
        self.home_page = GooglePage(driver=self.browser)
        self.home_page.GoTo(url=self.google_url)
        print(self.home_page.cookies_btns)

        self.home_page.search_textbox = 'Selenium Automation'

    def __call__(self):       
        self.LoadDrivers()
        self.NewGoogleSearch()

test_obj = DummyTestCase()
test_obj()

