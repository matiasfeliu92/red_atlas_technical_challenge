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

    def run(self):
        base_url = "https://www.zillow.com"
        
        # 1. NAVEGACIÓN INICIAL (Home)
        self.logger.info(f"INICIANDO NAVEGACIÓN EN: {base_url}")
        self.page.goto(base_url, wait_until="domcontentloaded")
        
        # Simular actividad y chequear captcha inicial
        self._human_behavior()
        self.captcha_solver.run()
        time.sleep(random.uniform(2, 4))

        # 2. NAVEGACIÓN AL OBJETIVO (Puerto Rico / Link Específico)
        self.logger.info(f"NAVEGANDO AL LINK OBJETIVO: {self.link}")
        self.page.goto(self.link, wait_until="domcontentloaded")
        
        # Zillow suele saltar el captcha justo aquí
        self._human_behavior()
        solved = self.captcha_solver.run()
        
        # Si el captcha se resolvió, esperamos un poco extra para la redirección
        if solved:
            time.sleep(random.uniform(4, 6))

        # 3. EXTRACCIÓN DE DATOS
        try:
            self.logger.info("BUSCANDO DATOS EN LA PÁGINA (__NEXT_DATA__)...")
            
            # Intentar localizar el script que contiene el JSON de las propiedades
            # Aumentamos un poco el timeout por si el captcha tardó en validar
            self.page.wait_for_selector("#__NEXT_DATA__", state="attached", timeout=15000)
            
            next_data_script = self.page.locator("#__NEXT_DATA__")
            raw_json = next_data_script.inner_html()
            data = json.loads(raw_json)
            data = data.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).get('searchResults', {}).get('listResults', [])
            
            self.logger.info("DATOS EXTRAÍDOS EXITOSAMENTE.")

            # 4. GUARDADO DE RESULTADOS
            # Creamos directorios y guardamos
            self.scraping_settings.create_dir("data", "for_sale")
            file_path = self.scraping_settings.get_dir("data", "for_sale", "data.json")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"ARCHIVO GUARDADO EN: {file_path}")

            # Opcional: Extraer un dato rápido para validar en el log
            # Generally in Zillow, the list of homes is in: 
            # data['props']['pageProps']['searchPageState']['cat1']['searchResults']['listResults']
            return data

        except Exception as e:
            self.logger.error(f"FALLO CRÍTICO EN LA EXTRACCIÓN: {str(e)}")
            # En caso de error, sacamos una captura de pantalla para debug
            self.page.screenshot(path="debug_error.png")
            self.logger.info("Captura de pantalla de error guardada como debug_error.png")
            return None