import random
import time
import json
from src.config.scraping_settings import ScrapingSettings
from src.config.logger import LoggerConfig
from src.utils.extract_elements import ExtractElements
from src.utils.solve_captcha import SolveCaptcha


class Scraping:
    def __init__(self):
        self.scraping_settings = ScrapingSettings()
        self.link = self.scraping_settings.BASE_LINK
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

        # Obtenemos la página (asegúrate de que get_browser_page use stealth_sync)
        self.page = self.scraping_settings.get_browser_page()

        self.extract_elements = ExtractElements(self.page)
        self.captcha_solver = SolveCaptcha(self.page)

    def _human_behavior(self):
        """Simula scroll y movimientos aleatorios para evitar detección."""
        self.logger.info("SIMULANDO COMPORTAMIENTO HUMANO...")
        try:
            # Scroll parcial
            self.page.evaluate(f"window.scrollTo(0, {random.randint(300, 700)})")
            time.sleep(random.uniform(1, 2))
            # Mover mouse a posición aleatoria
            self.page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            self.logger.warning(f"No se pudo ejecutar comportamiento humano: {e}")

    def scrap(self, path, filter_button_text):
        self.logger.info(f"""NAVEGANDO AL LINK OBJETIVO: {self.link + f"{path}"}""")
        self.page.goto(self.link + f"{path}", wait_until="domcontentloaded")
        self._human_behavior()
        solved = self.captcha_solver.run()

        if solved:
            time.sleep(random.uniform(4, 6))

        # 3. EXTRACCIÓN DE DATOS
        try:
            # Localizamos el contenedor de filtros
            div_filter_buttons = self.extract_elements.safe_find_element(
                self.scraping_settings.selectors["div"]
            )
            filter_buttons = div_filter_buttons.locator("div").all()

            for div in filter_buttons:
                span = div.locator("span").first
                span_text = span.inner_text()

                if filter_button_text in span_text:
                    self.logger.info(
                        f"FILTRO '{filter_button_text}' DETECTADO. PROCEDIENDO A EXTRACCIÓN..."
                    )
                    self.logger.info(f"SELECCIONANDO FILTRO: {filter_button_text}")
                    props = self.extract_elements.safe_find_element("h2")
                    self.logger.info(f"PROPS {filter_button_text.upper()}: {props.inner_text()}")

                    # --- FASE 1: EXTRAER Y GUARDAR FOR SALE ---
                    self.page.wait_for_selector(
                        "#__NEXT_DATA__", state="attached", timeout=15000
                    )
                    raw_json = self.page.locator("#__NEXT_DATA__").inner_html()

                    data_full = json.loads(raw_json)
                    list_props = (
                        data_full.get("props", {})
                        .get("pageProps", {})
                        .get("searchPageState", {})
                        .get("cat1", {})
                        .get("searchResults", {})
                        .get("listResults", [])
                    )
                    self.scraping_settings.create_dir("data", filter_button_text.lower().replace(" ", "_"))
                    data_path = self.scraping_settings.get_dir(
                        "data", filter_button_text.lower().replace(" ", "_"), f"data_page.json"
                    )
                    with open(data_path, "w", encoding="utf-8") as f:
                        json.dump(list_props, f, ensure_ascii=False, indent=4)
                    # self.logger.info(list_props)
                    self.logger.info(f"SE GUARDARON {len(list_props)} REGISTROS DE {filter_button_text.upper()} EN: {data_path}")
                    return list_props

        except Exception as e:
            self.logger.error(f"FALLO CRÍTICO EN LA EXTRACCIÓN: {str(e)}")
            self.page.screenshot(path="debug_error.png")
            return None
