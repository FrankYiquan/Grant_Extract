
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

import time

def get_ARC_grant(projectId):

    # FG started id is fellowship - fixed $75,000 in two years
    if projectId.startswith("FG") or projectId.startswith("fg"):
        fellowship_startDate = projectId.split('-')[1] if '-' in projectId else None
        return {
            "amount": 75000,
            "startDate": fellowship_startDate,
            "currency": "USD"
        }
    
    # for grant award or non-fellowship award
    # api protected - need web scraping

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://sloan.org/grants-database")
  

    #locate the input 
    search_input = driver.find_element(By.CSS_SELECTOR, "div.database-search input[name='keywords']")
    search_input.send_keys(projectId)
    search_input.send_keys(Keys.ENTER)
    time.sleep(2)

    amount = None
    startDate = None
    amount = None

    

    grants = driver.find_elements(By.CSS_SELECTOR, "ul.data-list > li")
    for grant in grants:
        amount = grant.find_element(By.CSS_SELECTOR, "div.amount").text.split("$")[-1].replace(",","").strip() if grant.find_element(By.CSS_SELECTOR, "div.amount") else None
        startDate = grant.find_element(By.CSS_SELECTOR, "div.year").text
    
    
    
    return{
        "amount": amount,
        "startDate": startDate,
        "currency": "USD",
    }




    


print(get_ARC_grant("FG-2022-18328"))
    
        