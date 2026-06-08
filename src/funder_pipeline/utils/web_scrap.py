from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

DRIVER_PATH = ChromeDriverManager().install()

def get_chrome_service():
    # print(DRIVER_PATH)
    return Service(DRIVER_PATH)

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(
        service=get_chrome_service(),
        options=options
    )