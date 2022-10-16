from collections import namedtuple,defaultdict
from re import A
import traceback,sys,time,os,glob,json, requests
import json
from jsonschema import validate
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
    def __init__(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_experimental_option('detach',False)
        #options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        self.driver = driver
    
    def GoTo(self,url):
        self.driver.get(url)

class BaseElement:

    def __init__(self,web_element,locator):
        self.web_element = web_element
        self.locator = locator

    def __str__(self):
        return str(self.web_element)

    def ReturnWebElement(self):
        return self.web_element

    def Click(self):
        element = WebDriverWait(self.driver,self.timeout).\
                    until(EC.element_to_be_clickable(mark= self.locator))
        element.click()
    
    def Clear(self):
        self.web_element.clear()

    def ClearManually(self,iter_num):
        for i in range(iter_num):
            self.web_element.send_keys(Keys.BACK_SPACE)
            self.web_element.send_keys(Keys.BACK_SPACE)
            self.web_element.send_keys(Keys.CONTROL + "a")
            self.web_element.send_keys(Keys.DELETE)

    def attribute(self,attr_name):
        return self.web_element.get_attribute(attr_name)
    
    def Enter(self):
        self.web_element.send_keys(Keys.ENTER)

    @property
    def text(self):
        if "input" in self.locator.value:
            return self.web_element.get_attribute('value')
        return self.web_element.text
    
    @text.setter
    def text(self,value):
        self.web_element.send_keys(value)


class GetElements:

    def __init__(self,driver,locator,timeout):
        self.driver = driver
        self.locator = locator
        self.timeout = timeout
        self.web_elements = self.driver.find_elements(self.locator.by,self.locator.value)
    
    def __len__(self):
        return len(self.web_elements)

    def __getitem__(self,s):
        iter_num = len(self.web_elements)
        if  s < 0 or s >= iter_num:
            raise IndexError
        else:
            return BaseElement(self.web_elements[s],self.locator)

class GetElement(BaseElement):
    def __init__(self,driver,locator,timeout):        
        self.driver = driver
        self.locator = locator
        self.timeout = timeout
        self.web_element = WebDriverWait(self.driver, self.timeout).\
                            until(EC.visibility_of_element_located(locator=self.locator))  
        BaseElement.__init__(self,self.web_element,self.locator)
                 

Locator = namedtuple('Locator',['by','value'])

class GetElementsDescriptor:

    def __init__(self,locator,timeout=5, mult_elems= False):
        self.locator = locator
        self.timeout = timeout
        self.mult_elems = mult_elems
    
    def __get__(self,instance,owner_class):
        if self.mult_elems is True:
            return GetElements(driver=instance.driver, locator= self.locator, timeout=self.timeout)
        return GetElement(driver=instance.driver, locator= self.locator, timeout=self.timeout)

class GooglePage(BasePage):
    search_textbox = GetElementsDescriptor(Locator(by=By.XPATH,\
                                                   value ="//input[@name='q']/../input"))

    cookies_btns = GetElementsDescriptor(Locator(by=By.XPATH,\
                                                   value ="//div[contains(@class,'QS5gu sy4vM')]"))
    def __init__(self):
        super().__init__()

class TechStepPage(BasePage):
    input_1 = GetElementsDescriptor(Locator(by=By.CSS_SELECTOR,\
                                                   value ="input[id='r1Input']"))

    answer_1 = GetElementsDescriptor(Locator(by=By.CSS_SELECTOR,\
                                                   value ="button[id='r1Btn']"))

    elems =  GetElementsDescriptor(Locator(by=By.TAG_NAME,\
                                                   value ="input"),mult_elems=True)   
    def __init__(self):
        super().__init__() 

class BaseTestCase:

    def __init__(self):
        self.google_url = 'https://www.google.com/'
        self.techstep_url = 'https://techstepacademy.com/trial-of-the-stones'
    
    def DummyTechStep(self):
        self.techstep_page = TechStepPage()
        self.techstep_page.GoTo(url=self.techstep_url)
        self.techstep_page.input_1.text = 'rock'
        self.techstep_page.answer_1.Click()
        elem = self.techstep_page.elems[1]
        print(elem.text)
        elem.text ='aaa'
        print(elem.text)

    def NewGoogleSearch(self):
        self.google_page = GooglePage()
        self.google_page.GoTo(url=self.google_url)
        self.google_page.search_textbox = 'Selenium Automation'

    def __call__(self):       
        #self.NewGoogleSearch()
        self.DummyTechStep()

# obj = BaseTestCase()
# obj()

