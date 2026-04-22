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

    # def run(self):
    #     base_url = "https://www.zillow.com"
        
    #     # 1. NAVEGACIÓN INICIAL (Home)
    #     self.logger.info(f"INICIANDO NAVEGACIÓN EN: {base_url}")
    #     self.page.goto(base_url, wait_until="domcontentloaded")
        
    #     # Simular actividad y chequear captcha inicial
    #     self._human_behavior()
    #     self.captcha_solver.run()
    #     time.sleep(random.uniform(2, 4))

    #     # 2. NAVEGACIÓN AL OBJETIVO (Puerto Rico / Link Específico)
    #     self.logger.info(f"NAVEGANDO AL LINK OBJETIVO: {self.link}")
    #     self.page.goto(self.link, wait_until="domcontentloaded")
        
    #     # Zillow suele saltar el captcha justo aquí
    #     self._human_behavior()
    #     solved = self.captcha_solver.run()
        
    #     # Si el captcha se resolvió, esperamos un poco extra para la redirección
    #     if solved:
    #         time.sleep(random.uniform(4, 6))

    #     # 3. EXTRACCIÓN DE DATOS
    #     try:
    #         div_filter_buttons = self.extract_elements.safe_find_element(self.scraping_settings.selectors['div'])
    #         filter_buttons = div_filter_buttons.locator("div").all()

    #         for div in filter_buttons:
    #             span = div.locator("span").first
    #             span_text = span.inner_text()

    #             self.logger.info(f"SPAN ENCONTRADO: {span_text}")
    #             if "For sale" in span_text:
    #                 self.logger.info("SELECCIONANDO FILTRO: For sale")
    #                 props_for_sale = self.extract_elements.safe_find_element("h2")
    #                 self.logger.info(f"PROPS FOR SALE: {props_for_sale.inner_text()}")
    #                 self.logger.info("BUSCANDO DATOS EN LA PÁGINA (__NEXT_DATA__)... FOR SALE")
    #                 self.page.wait_for_selector("#__NEXT_DATA__", state="attached", timeout=15000)
    #                 next_data_script = self.page.locator("#__NEXT_DATA__")
    #                 raw_json = next_data_script.inner_html()
    #                 data = json.loads(raw_json)
    #                 data = data.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).get('searchResults', {}).get('listResults', [])
                    
    #                 self.logger.info("DATOS EXTRAÍDOS EXITOSAMENTE.")

    #                 # 4. GUARDADO DE RESULTADOS
    #                 # Creamos directorios y guardamos
    #                 self.scraping_settings.create_dir("data", "for_sale")
    #                 file_path = self.scraping_settings.get_dir("data", "for_sale", "data.json")
                    
    #                 with open(file_path, "w", encoding="utf-8") as f:
    #                     json.dump(data, f, ensure_ascii=False, indent=4)
                    
    #                 self.logger.info(f"ARCHIVO GUARDADO EN: {file_path}")
    #                 div.click()
    #                 self.logger.info("BUSCANDO INPUT/OPCION CON TEXTO 'FOR RENT'...")
    #                 for_rent_option = self.page.locator(
    #                     "label:has-text('For rent'), label:has-text('For Rent'), "
    #                     "span:has-text('For rent'), span:has-text('For Rent')"
    #                 ).first

    #                 try:
    #                     for_rent_option.wait_for(state="visible", timeout=5000)
    #                     for_rent_option.click()
    #                 except Exception:
    #                     self.logger.info("NO SE PUDO HACER CLICK POR TEXTO, USANDO FALLBACK #isForRent")
    #                     self.page.locator("#isForRent").click(force=True)

    #                 self.logger.info("FILTRO FOR RENT SELECCIONADO. ESPERANDO ACTUALIZACION...")
    #                 time.sleep(random.uniform(2, 4))
    #                 self.captcha_solver.run()
    #                 props_for_rent = self.extract_elements.safe_find_element("h2")
    #                 self.logger.info(f"PROPS FOR RENT: {props_for_rent.inner_text()}")
    #                 self.logger.info("BUSCANDO DATOS EN LA PÁGINA (__NEXT_DATA__)... FOR RENT")
    #                 self.page.wait_for_selector("#__NEXT_DATA__", state="attached", timeout=15000)

    #                 # Esperar a que __NEXT_DATA__ cambie respecto al snapshot de For Sale.
    #                 raw_json_rent = None
    #                 rent_timeout = time.time() + 20
    #                 while time.time() < rent_timeout:
    #                     candidate = self.page.locator("#__NEXT_DATA__").inner_html()
    #                     if candidate != raw_json:
    #                         raw_json_rent = candidate
    #                         break
    #                     time.sleep(0.7)

    #                 # Fallback: usar el ultimo valor disponible aunque no haya cambiado.
    #                 if not raw_json_rent:
    #                     self.logger.warning("__NEXT_DATA__ no cambio tras seleccionar For Rent; usando snapshot actual")
    #                     raw_json_rent = self.page.locator("#__NEXT_DATA__").inner_html()

    #                 data_rent = json.loads(raw_json_rent)
    #                 data_rent = data_rent.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).get('searchResults', {}).get('listResults', [])

    #                 self.logger.info("DATOS FOR RENT EXTRAIDOS EXITOSAMENTE.")

    #                 if data_rent == data:
    #                     self.logger.warning("FOR RENT ES IGUAL A FOR SALE. NO SE SOBRESCRIBE data/for_rent/data.json")
    #                 else:
    #                     self.scraping_settings.create_dir("data", "for_rent")
    #                     rent_path = self.scraping_settings.get_dir("data", "for_rent", "data.json")
    #                     with open(rent_path, "w", encoding="utf-8") as f:
    #                         json.dump(data_rent, f, ensure_ascii=False, indent=4)

    #                     self.logger.info(f"ARCHIVO FOR RENT GUARDADO EN: {rent_path}")

    #     except Exception as e:
    #         self.logger.error(f"FALLO CRÍTICO EN LA EXTRACCIÓN: {str(e)}")
    #         # En caso de error, sacamos una captura de pantalla para debug
    #         self.page.screenshot(path="debug_error.png")
    #         self.logger.info("Captura de pantalla de error guardada como debug_error.png")
    #         return None

    def run(self):
        base_url = "https://www.zillow.com"
        
        # 1. Navegación e inicio
        self.logger.info(f"INICIANDO NAVEGACIÓN EN: {base_url}")
        self.page.goto(base_url, wait_until="domcontentloaded")
        self._human_behavior()
        self.captcha_solver.run()

        self.logger.info(f"NAVEGANDO AL LINK OBJETIVO: {self.link}")
        self.page.goto(self.link, wait_until="domcontentloaded")
        self._human_behavior()
        solved = self.captcha_solver.run()
        
        if solved:
            time.sleep(random.uniform(4, 6))

        # 3. EXTRACCIÓN DE DATOS
        try:
            # Localizamos el contenedor de filtros
            div_filter_buttons = self.extract_elements.safe_find_element(self.scraping_settings.selectors['div'])
            filter_buttons = div_filter_buttons.locator("div").all()

            for div in filter_buttons:
                span = div.locator("span").first
                span_text = span.inner_text()

                if "For sale" in span_text:
                    self.logger.info("FILTRO 'FOR SALE' DETECTADO. PROCEDIENDO A EXTRACCIÓN...")
                    self.logger.info("SELECCIONANDO FILTRO: For sale")
                    props_for_sale = self.extract_elements.safe_find_element("h2")
                    self.logger.info(f"PROPS FOR SALE: {props_for_sale.inner_text()}")
                    
                    # --- FASE 1: EXTRAER Y GUARDAR FOR SALE ---
                    self.page.wait_for_selector("#__NEXT_DATA__", state="attached", timeout=15000)
                    raw_json_sale = self.page.locator("#__NEXT_DATA__").inner_html()
                    
                    data_sale_full = json.loads(raw_json_sale)
                    list_sale = data_sale_full.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).get('searchResults', {}).get('listResults', [])
                    self.logger.info(f"DATOS FOR SALE EXTRAÍDOS EXITOSAMENTE:    \n{list_sale}")
                    self.scraping_settings.create_dir("data", "for_sale")
                    sale_path = self.scraping_settings.get_dir("data", "for_sale", "data.json")
                    with open(sale_path, "w", encoding="utf-8") as f:
                        json.dump(list_sale, f, ensure_ascii=False, indent=4)
                    
                    self.logger.info(f"DATOS FOR SALE GUARDADOS EN: {sale_path}")

                    # --- FASE 2: CAMBIAR A FOR RENT ---
                    self.logger.info("ABRIENDO MENÚ PARA CAMBIAR A 'FOR RENT'...")
                    div.click() # Click en el botón que dice "For sale" para desplegar opciones
                    time.sleep(random.uniform(1, 2))

                    # Buscamos el input/opción "For Rent"
                    # Usamos el ID directamente con click forzado ya que suele estar oculto tras un label
                    self.page.locator("#isForRent").click(force=True)
                    self.logger.info("CLICK EN 'FOR RENT' REALIZADO. ESPERANDO ACTUALIZACIÓN DEL SCRIPT...")
                    
                    # --- FASE 3: VALIDAR CAMBIO DE DATA ---
                    # Esperamos hasta que el contenido de __NEXT_DATA__ sea distinto al de Sale
                    raw_json_rent = None
                    max_wait = time.time() + 45
                    
                    while time.time() < max_wait:
                        props_for_rent = self.extract_elements.safe_find_element("h2")
                        self.logger.info(f"PROPS FOR RENT: {props_for_rent.inner_text()}")                    
                        current_content = self.page.locator("#__NEXT_DATA__").inner_html()
                        # Verificamos si el JSON ya no es el mismo que el de Sale
                        if current_content != raw_json_sale:
                            raw_json_rent = current_content
                            self.logger.info("CAMBIO EN __NEXT_DATA__ DETECTADO!")
                            break
                        time.sleep(1)
                    
                    if not raw_json_rent:
                        self.logger.warning(f"EL SCRIPT NO CAMBIÓ TRAS {max_wait}s. INTENTANDO EXTRACCIÓN DIRECTA.")
                        raw_json_rent = self.page.locator("#__NEXT_DATA__").inner_html()

                    # --- FASE 4: GUARDAR FOR RENT ---
                    data_rent_full = json.loads(raw_json_rent)
                    list_rent = data_rent_full.get('props', {}).get('pageProps', {}).get('searchPageState', {}).get('cat1', {}).get('searchResults', {}).get('listResults', [])

                    # Validación de seguridad: no guardar si la data sigue siendo idéntica (error de carga)
                    if list_rent == list_sale and len(list_sale) > 0:
                        self.logger.error("LA DATA DE RENT ES IDÉNTICA A SALE. EL CAMBIO DE FILTRO NO SE REFLEJÓ.")
                    else:
                        self.scraping_settings.create_dir("data", "for_rent")
                        rent_path = self.scraping_settings.get_dir("data", "for_rent", "data.json")
                        with open(rent_path, "w", encoding="utf-8") as f:
                            json.dump(list_rent, f, ensure_ascii=False, indent=4)
                        self.logger.info(f"DATOS FOR RENT GUARDADOS EN: {rent_path}")
                    
                    # Salimos del bucle una vez procesados ambos
                    break

        except Exception as e:
            self.logger.error(f"FALLO CRÍTICO EN LA EXTRACCIÓN: {str(e)}")
            self.page.screenshot(path="debug_error.png")
            return None