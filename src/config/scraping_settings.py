from playwright_stealth import stealth
import logging

from playwright.sync_api import sync_playwright, Page

from src.config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class ScrapingSettings(Settings):

    def __init__(self):
        super().__init__()
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        self.selectors = {
            # 'boton_pulsar_y_mantener_pulsado': "xpath=//div[contains(@class, 'px-captcha') and contains(., 'Press')]",
            'boton_pulsar_y_mantener_pulsado': "xpath=//div[.//p[contains(text(), 'Press & Hold') or contains(text(), 'Pulsar')]]",
            'div': 'div.filter-buttons',
            'apply_button': "xpath=//button[.//span[text()='Apply']]",
            'inputs': {
                'for_sale': '#isForSaleByAgent_isForSaleByOwner_isNewConstruction_isComingSoon_isAuction_isForSaleForeclosure_isPreMarketForeclosure_isPreMarketPreForeclosure',
                'for_rent': '#isForRent',
            },
            'div_boton_tipo_propiedad': '[data-test="more-filters-button"]',
        }
        self._playwright = None
        self._browser = None
        self.web_paths = [
            {"path": "sales", "filter": "For sale"}, 
            {"path": "rentals", "filter": "For rent"}
        ]


    def get_browser_page(self) -> Page:
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=False, # Mantener en False para Zillow
            args=[
                "--disable-blink-features=AutomationControlled",
                "--window-size=1920,1080"
            ],
        )
        context = self._browser.new_context(
            user_agent=self.USER_AGENT,
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        
        # # CRÍTICO: Aplicar stealth para ocultar huellas de automatización
        # stealth(page)
        
        return page

    def close(self):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()