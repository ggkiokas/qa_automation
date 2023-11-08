import os
import selenium
import time
from frontend.selenium_wd.src.utilities.locator import Locator
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from typing import Union, Tuple

from frontend.selenium_wd.src.utilities.general_utils import (
    handle_timeout_exception,
    sleep_before_action,
    handle_click_intercepted_exception,
    retry_fun,
)
from common.constants import *


class BaseElement:
    def __init__(self, driver, web_element, locator, timeout, name, raise_exc):
        self.driver = driver
        self.web_element = web_element
        self.locator = locator
        self.timeout = timeout
        self.name = name
        self.raise_exc = raise_exc
        self.scroll_down()

    @retry_fun(ExceptionToCheck=MoveTargetOutOfBoundsException, tries=3, delay=2)
    def scroll_down(self):
        if "file" != self.web_element.get_attribute(
            "type"
        ):  # can not apply move actions to elements that upload data
            actions = ActionChains(self.driver)
            actions.move_to_element(self.web_element).perform()

    def __getattr__(
        self, attr
    ):  # to get WebElement attributes. It is used to delegate attribute access to self.web_element (an instance of WebElement) if the attribute is not found in BaseElement
        return getattr(self.web_element, attr)

    def __str__(self):
        return str(self.web_element)

    def Click(self):
        @handle_click_intercepted_exception(self.name, self.locator)
        @handle_timeout_exception(
            "click", self.name, self.locator, self.timeout, self.raise_exc
        )
        def click_wrapper():
            try:
                wait_element(self.web_element).click()
            except (
                selenium.common.exceptions.StaleElementReferenceException
            ):  # to overcome this exception I research the element based on the locator or I refresh the page
                time.sleep(1)
                wait_element(self.locator.as_tuple()).click()

        def wait_element(mark_option: Union[Tuple[str, str], WebElement]) -> None:
            web_element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(mark=mark_option)
            )
            return web_element

        return click_wrapper()

    def click_explicit(self):
        self.web_element.click()

    def Clear(self):
        self.web_element.clear()
        self.web_element.send_keys("")

    def clear_manually(self, chars=None):
        # If chars is not provided, the length of the text in the web_element is calculated.
        # Here, we use self.text to call the 'text' property of the BaseElement class.
        # If we were to use self.web_element.text, it would reference the 'text' attribute of the WebElement class instead so not what we want.
        if chars is None:
            chars = len(self.text)
        for i in range(chars):
            self.web_element.send_keys(Keys.BACK_SPACE)

    @sleep_before_action(1)  # maybe re-search the element instead of sleep
    def press_key_on_element(self, key):  # key can be Enter, tab, Down, ESCAPE etc
        key_value = getattr(Keys, key.upper())
        self.web_element.send_keys(key_value)

    @property
    def is_selected(self):
        return self.web_element.is_selected()

    @property
    def is_enabled(self):
        return self.web_element.is_enabled()

    @property
    def is_displayed(self):
        return self.web_element.is_displayed()

    @property
    def has_cursor(self):
        return self.driver.switch_to.active_element == self.web_element

    @property
    def text(self):
        if "input" in self.locator.value:
            return self.web_element.get_attribute("value")
        return self.web_element.text

    @text.setter
    def text(self, value):
        self.web_element.send_keys(value)


class GetElements:
    def __init__(self, driver, locator, timeout, name, raise_exc):
        self.driver = driver
        self.locator = locator
        self.timeout = timeout
        self.name = name
        self.raise_exc = raise_exc
        self.web_elements = self.wait_and_find_elements()

    def wait_and_find_elements(self):
        """
        This function can return:
        - List of WebElement: A list of WebElement instances when the elements are found
        - None: None when no elements are found because exception is suppressed (raise_exc=False)
        """

        @handle_timeout_exception(
            "select", self.name, self.locator, self.timeout, self.raise_exc
        )
        def wait_wrapper():
            conditions = EC.any_of(
                EC.visibility_of_all_elements_located(self.locator.as_tuple()),
                EC.presence_of_all_elements_located(
                    (self.locator.by, self.locator.value)
                ),
            )
            web_elements = WebDriverWait(self.driver, self.timeout).until(conditions)

            return web_elements

        return wait_wrapper()

    def __len__(self):
        if self.web_elements is not None:
            return len(self.web_elements)

    def __getitem__(self, s):
        if self.web_elements is None:
            raise ValueError("No web elements found.")

        # If the argument is an integer, get the corresponding element
        if isinstance(s, int):
            if s < 0 or s >= len(self.web_elements):
                raise IndexError
            return BaseElement(
                self.driver,
                self.web_elements[s],
                self.locator,
                self.timeout,
                self.name,
                self.raise_exc,
            )
        # If the argument is a slice, get a sublist
        elif isinstance(s, slice):
            start = s.start or 0
            stop = s.stop or len(self.web_elements)
            step = s.step or 1

            # Return a list of BaseElement instances
            return [
                BaseElement(
                    self.driver,
                    self.web_elements[i],
                    self.locator,
                    self.timeout,
                    self.name,
                    self.raise_exc,
                )
                for i in range(start, stop, step)
            ]

        else:
            raise TypeError("Invalid argument type.")


class GetElement(BaseElement):
    def __init__(self, driver, base_element, locator, timeout, name, raise_exc):
        self.driver = driver
        self.base_element = base_element
        self.locator = locator
        self.timeout = timeout
        self.name = name
        self.raise_exc = raise_exc
        self.web_element = self.wait_and_find_element()
        if isinstance(self.web_element, WebElement):
            super().__init__(
                self.driver,
                self.web_element,
                self.locator,
                self.timeout,
                self.name,
                self.raise_exc,
            )

    def wait_and_find_element(self) -> Union[WebElement, bool, None]:
        """
        This function can return:
        - WebElement: A WebElement instance when the element is found
        - bool: A boolean value when the title of the page is found
        - None: None when no element is found because exception is suppressed (raise_exc=False)
        """

        @handle_timeout_exception(
            "select",
            self.name,
            self.locator,
            self.timeout,
            self.raise_exc,
            base_element=self.base_element,
        )
        def wait_wrapper():
            if self.base_element is None:
                web_element = wait_element(
                    locator=self.locator, base_web_element=self.driver
                )
            else:
                # Locators that use base_element must start with the pattern: "./blabla"
                base_web_element = wait_element(
                    locator=self.base_element.locator, base_web_element=self.driver
                )
                web_element = wait_element(
                    locator=self.locator, base_web_element=base_web_element
                )

            return web_element

        def wait_element(locator, base_web_element):
            if self.locator.by == TITLE:
                conditions = EC.title_is(locator.value)
            else:
                conditions = EC.any_of(
                    EC.visibility_of_element_located(locator=locator.as_tuple()),
                    EC.presence_of_element_located(locator.as_tuple()),
                )

            web_element = WebDriverWait(base_web_element, self.timeout).until(
                conditions
            )

            return web_element

        return wait_wrapper()


class BaseElementDescriptor:
    def __init__(self, by, value, timeout=os.getenv("TIMEOUT_UI"), raise_exc=True):
        self.locator = Locator(by=by, value=value)
        self.timeout = timeout
        self.raise_exc = raise_exc
        self.original_value = self.locator.value

    def __set_name__(self, owner_class, name):
        self.property_name = name

    def __set__(self, instance, locator_value):
        if isinstance(locator_value, str):
            updated_value = self.original_value.replace("_replaceme_", locator_value)
            self.locator.value = updated_value
        else:
            raise ValueError(
                "Invalid locator value. Expected a string. Received {locator_value}"
            )


class GetMultElementsDescriptor(BaseElementDescriptor):
    def __get__(self, instance, owner_class):
        return GetElements(
            driver=instance.driver,
            locator=self.locator,
            timeout=self.timeout,
            name=self.property_name,
            raise_exc=self.raise_exc,
        )


class GetElementDescriptor(BaseElementDescriptor):
    def __init__(self, *args, base_element=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_element = base_element

    def __get__(self, instance, owner_class):
        return GetElement(
            driver=instance.driver,
            base_element=self.base_element,
            locator=self.locator,
            timeout=self.timeout,
            name=self.property_name,
            raise_exc=self.raise_exc,
        )


# Change the line:
#         if "input" in self.locator.value:
# @property
# def text(self):
#     if self.web_element.tag_name == "input":
#         return self.web_element.get_attribute("value")
#     return self.web_element.text

# @property
# def text(self):
#     if self.web_element.tag_name == "input":
#         input_type = self.web_element.get_attribute("type")
#         if input_type == "text":
#             return self.web_element.get_attribute("value")
#         # Add more conditions for other input types if needed
#     return self.web_element.text
