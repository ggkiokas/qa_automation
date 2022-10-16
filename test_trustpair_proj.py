# crontab for execution of tests every Monday, Wednesday, Friday
# extra validation for jsons with schema

import json,requests, pytest, warnings, re
from collections import defaultdict
from selenium_arch import GetElementsDescriptor,Locator,BasePage
from selenium.webdriver.common.by import By

class TrustPairPage(BasePage):
    links =  GetElementsDescriptor(Locator(by=By.TAG_NAME,\
                                                   value ="a"),mult_elems=True)
    json_content =  GetElementsDescriptor(Locator(by=By.TAG_NAME,\
                                                   value ="body"))

    def __init__(self):
        super().__init__() 

class TrustPairProject:

    def SetUpFun(self):
        self.url = 'https://xkcd.com/about/'
        self.url_status_dict = {}
        self.json_contents = {}
        self.json_urls = []
        self.mail_addresses = []

    def CollectJsonsContents(self):
        for json_url in self.json_urls:
            self.about_page.GoTo(url=json_url)
            json_welem = self.about_page.json_content
            self.json_contents[json_url]= json_welem.text

    def CollectUrlsAndStatus(self,url_path):
        try:
            request_response = requests.head(url_path)
            status_code = request_response.status_code          
            self.url_status_dict[url_path] = str(status_code)
        except Exception as e:
            self.url_status_dict[url_path] = str(e)

    def __call__(self):
        self.SetUpFun()
        self.about_page = TrustPairPage()      
        self.about_page.GoTo(url=self.url)
        links = self.about_page.links
        for link in links:
            url_path = link.attribute("href")
            if str(url_path).startswith('mail'):
                self.mail_addresses.append(url_path)
                continue
            if str(url_path).endswith('.json'):
                self.json_urls.append(url_path)
            self.CollectUrlsAndStatus(url_path)
        self.CollectJsonsContents()

obj = TrustPairProject()
obj()

@pytest.mark.parametrize("url_path, status_code", list(tuple(obj.url_status_dict.items())))
def test_status_of_urls(url_path, status_code):
    if status_code.startswith('4') or status_code.startswith('5'):
        raise Exception(f"Invalid status {status_code} for url: {url_path}")
    elif status_code.startswith('3'):
        warnings.warn(UserWarning(f"Warning status {status_code} for url: {url_path}"))
    elif status_code.startswith('2'):
       pass
    else:
        raise Exception(f"Invalid status {status_code} for url: {url_path}")

@pytest.mark.parametrize("json_path, json_content", list(tuple(obj.json_contents.items())))
def test_json_contents(json_path,json_content):
    try:
        json.loads(json_content) # put JSON-data to a variable
    except json.decoder.JSONDecodeError:
        raise Exception(f"Invalid JSON with link: {json_path}") # in case json is invalid

@pytest.mark.parametrize("mail_address", obj.mail_addresses)
def test_mail_addresses(mail_address):
    if 'mailto:' not in mail_address:
        raise Exception(f"Callback mailto is not present at: {mail_address}")
    mail_address = mail_address.replace('mailto:','')
    mail_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(mail_regex, mail_address)):
        raise Exception(f" Invalid mail address {mail_address}")
