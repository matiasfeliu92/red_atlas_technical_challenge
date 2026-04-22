from src.config.scraping_settings import ScrapingSettings
from src.scripts.scraping import Scraping

if __name__ == "__main__":
    settings = ScrapingSettings()
    web_paths = settings.web_paths
    scraping = Scraping()
    for path in web_paths:
        print(f"INICIANDO SCRAPING PARA: {path}")
        scraping.scrap(path["path"], path["filter"])