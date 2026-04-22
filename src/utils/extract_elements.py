from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

from src.config.logger import LoggerConfig

class ExtractElements:
    def __init__(self, page: Page):
        self.page = page
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    def safe_find_element(self, selector: str, multiple=False, timeout=20000):
        try:
            if multiple:
                self.logger.info("MULTIPLE")
                locator = self.page.locator(selector)
                locator.first.wait_for(state="visible", timeout=timeout)
                return locator.all()
            else:
                self.logger.info("ELEMENT")
                locator = self.page.locator(selector).first
                locator.wait_for(state="visible", timeout=timeout)
                return locator
        except PlaywrightTimeoutError as e:
            self.logger.error(f"[TimeoutError] {str(e)} | selector={selector}")
            return None
        except Exception as e:
            self.logger.error(f"[Exception] {str(e)} | selector={selector}")
            return None