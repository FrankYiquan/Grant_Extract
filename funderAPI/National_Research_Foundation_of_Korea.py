from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

import time

def get_National_Research_Foundation_of_Korea_grant(projectId):
     
    #normalize projectId
    projectId = projectId.lower() 
    projectId = projectId.replace("nrf-", "") if "nrf-" in projectId else projectId
    projectId = projectId.replace("nrf ", "") if "nrf " in projectId else projectId


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    #go to the grant display page
    url = f"https://www.ntis.go.kr/ThSearchProjectList.do?searchWord={projectId}&oldSearchWord={projectId}&resultSearch=&gubun=link&sort=SS01/DESC,RANK/DESC"
    driver.get(url)

    

    try:
        elements = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.listType.originPjt"))
        )
    except TimeoutException:
        elements = {}  # default if not found

    amount = 0
    startDate = None
    title = None
    

    for grant in elements:
        title = grant.find_element(By.CSS_SELECTOR, "a.announce").text.strip()
        grant_year = grant.find_element(By.CSS_SELECTOR,"p.lastPy.slash").text.strip()
        #get the earlies year - start date
        if startDate == None or (grant_year and grant_year < startDate):
            startDate = grant_year
        
        #amount is the last element at the list
        last_p = grant.find_element(By.XPATH, ".//div[@class='listDetail'][1]/p[last()]").text.strip()
        one_amount = last_p.split("(")[0].replace(",", "").strip()
        print(grant_year,":", one_amount)
       

        #sum up all the amounts if there are multiple grants
        amount += int(one_amount)
    
    return{
        "title": title,
        "amount": amount,
        "start_date": startDate,
        "currency": "KRW"
    }

      
            


# print(get_National_Research_Foundation_of_Korea_grant("(NRF 2017R1E1A1A01074980"))


