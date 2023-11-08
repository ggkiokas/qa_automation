from functools import wraps
import selenium
from selenium.common.exceptions import StaleElementReferenceException
import re
from datetime import datetime as dt, timedelta
import time, os
import random
from common.constants import *
from common.generic_utils import *
from typing import Tuple, Optional
from common.log_config import configure_logger

logger = configure_logger(__name__)


import time
from functools import wraps


def retry_fun(ExceptionToCheck=StaleElementReferenceException, tries=3, delay=3):
    """
    Retry calling the decorated function.

    :param ExceptionToCheck: the exception to check (default is StaleElementReferenceException).
    :param tries: number of times to try before giving up.
    :param delay: delay between retries in seconds.
    """

    def deco_retry(func):
        @wraps(func)
        def f_retry(*args, **kwargs):
            mtries = tries
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except ExceptionToCheck as e:
                    time.sleep(delay)
                    mtries -= 1
                    logger.debug(
                        f"Exception '{str(e)}' occurred. Trying again {mtries} more times"
                    )
            return func(*args, **kwargs)  # last try

        return f_retry

    return deco_retry


def handle_timeout_exception(
    action, name, locator, timeout, raise_exc, base_element=None
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except selenium.common.exceptions.TimeoutException:
                if raise_exc is True:
                    base_element_locator = (
                        base_element.locator if base_element is not None else "N/A"
                    )
                    raise GenericSeleniumException(
                        f"\n Timeout when trying to {action} \n element:   {name}    \n with locator {locator} \n within {timeout} sec. \n Base Element has locator {base_element_locator}"
                    ) from None
                else:
                    return None

        return wrapper

    return decorator


def handle_click_intercepted_exception(name, locator):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except selenium.common.exceptions.ElementClickInterceptedException:
                raise GenericSeleniumException(
                    f"\n ElementClickInterceptedException on \n element: {name} \n with locator {locator} \n A new pop-up probably caused the error"
                ) from None

        return wrapper

    return decorator


def sleep_before_action(delay):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(delay)
            func(*args, **kwargs)

        return wrapper

    return decorator


def isolate_text_in_locators(locator_value):
    text_locator = ""
    single_quotes_pattern = "'([^']*)'"
    double_quotes_pattern = '"([^"]*)"'

    single_quotes_match = re.search(single_quotes_pattern, locator_value)
    double_quotes_match = re.search(double_quotes_pattern, locator_value)

    if single_quotes_match:
        text_locator = single_quotes_match.group(1)
    elif double_quotes_match:
        text_locator = double_quotes_match.group(1)

    return text_locator


def select_box_options(page, web_element, items_ls):
    for item in items_ls:
        setattr(page, web_element, item)
        getattr(page, web_element).Click()

        is_selected = WHITE_FONT in getattr(page, web_element).value_of_css_property(
            "color"
        )
        assert is_selected, f"{item} is not selected"


def add_cookie(driver):
    expiration_time = dt.now() + timedelta(seconds=1)
    driver.add_cookie(
        {
            "name": "session",
            "value": "your_session_value",
            "expires": expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    # Perform your tests within the shortened session duration
    # ...

    # Wait for the session to expire
    driver.implicitly_wait(2)  # Wait for 2 seconds
