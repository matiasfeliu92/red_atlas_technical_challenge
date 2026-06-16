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
        print(f"""INICIANDO SCRAPING PARA: {path["path"]}""")
        for page_number in range(1,8):
            url = path["path"] + f"/{page_number}_p"
            scraped_data = scraping.scrap(url, path["filter"])
            load_data.save_json_file(path["path"], scraped_data, page_number)