import time
import random
from src.config.logger import LoggerConfig

class SolveCaptcha:
    def __init__(self, page):
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.page = page

    def run(self):
        self.logger.info("BUSCANDO BOTÓN CAPTCHA (MODO AGRESIVO)...")
        time.sleep(4) # Espera a que el reto se asiente

        # JS para encontrar el botón en cualquier parte (Frames + Shadow DOM)
        js_finder = """() => {
            const findInRoot = (root) => {
                // Selectores posibles de PerimeterX
                const selectors = [
                    'div[role="button"][aria-label*="Press"]',
                    'div[role="button"][aria-label*="Pulsar"]',
                    'div#px-captcha-button',
                    '[aria-label*="Hold"]'
                ];
                for (let s of selectors) {
                    let el = root.querySelector(s);
                    if (el) return el;
                }
                // Buscar recursivamente en Shadow DOMs
                const children = root.querySelectorAll('*');
                for (let child of children) {
                    if (child.shadowRoot) {
                        const found = findInRoot(child.shadowRoot);
                        if (found) return found;
                    }
                }
                return null;
            };

            const btn = findInRoot(document);
            if (btn) {
                const rect = btn.getBoundingClientRect();
                return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
            }
            return null;
        }"""

        target_info = None
        target_context = self.page

        # 1. Buscar en página principal
        target_info = self.page.evaluate(js_finder)

        # 2. Si no está, buscar en todos los frames
        if not target_info:
            for frame in self.page.frames:
                try:
                    info = frame.evaluate(js_finder)
                    if info and info['width'] > 0:
                        target_info = info
                        target_context = frame
                        self.logger.info(f"CAPTCHA LOCALIZADO EN IFRAME: {frame.url[:50]}...")
                        break
                except:
                    continue

        if not target_info:
            self.logger.info("NO SE DETECTÓ CAPTCHA VISIBLE.")
            return False

        # 3. Interacción física con el mouse
        try:
            # Calculamos el centro relativo al viewport
            # Nota: Si está en un iframe, necesitamos las coordenadas absolutas
            # Playwright maneja las coordenadas del mouse relativas al viewport principal
            box = target_info
            
            # Si el frame tiene coordenadas, hay que sumarlas (pero evaluate devuelve rect relativo al frame)
            # Para simplificar, forzamos un scroll al botón:
            target_context.locator('div[role="button"]').first.scroll_into_view_if_needed()
            
            # Re-obtener posición tras scroll
            box = target_context.locator('div[role="button"]').first.bounding_box()

            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2

            self.page.mouse.move(x, y, steps=25)
            self.logger.info("PRESIONANDO BOTÓN...")
            self.page.mouse.down()
            
            # Tiempo humano (PerimeterX requiere > 10s)
            duration = random.uniform(10.5, 12.5)
            time.sleep(duration)
            
            self.page.mouse.up()
            self.logger.info("BOTÓN LIBERADO. ESPERANDO VALIDACIÓN...")
            time.sleep(5)
            return True

        except Exception as e:
            self.logger.error(f"FALLO EN INTERACCIÓN: {e}")
            return False