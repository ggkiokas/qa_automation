from selenium.webdriver.common.by import By


class Locator:
    def __init__(self, by, value):
        self._by = by
        self.value = value

    @property
    def by(self):
        if self._by.lower() == "xpath":
            return By.XPATH
        elif self._by.lower() == "css":
            return By.CSS_SELECTOR
        elif self._by.lower() == "id":
            return By.ID
        elif self._by.lower() == "title":
            return "title"

        return self._by

    def __repr__(self):
        return f"Locator(by='{self.by}', value='{self.value}')"

    def as_tuple(self):
        return self.by, self.value
