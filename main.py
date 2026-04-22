from src.config.manage_db import ManageDB
from src.scripts.load_data import LoadData
from src.config.scraping_settings import ScrapingSettings
from src.scripts.scraping import Scraping

if __name__ == "__main__":
    settings = ScrapingSettings()
    load_data = LoadData(ManageDB())
    web_paths = settings.web_paths
    scraping = Scraping()
    for path in web_paths:
        print(f"INICIANDO SCRAPING PARA: {path}")
        scraped_data = scraping.scrap(path["path"], path["filter"])
        load_data.insert_listings(scraped_data)