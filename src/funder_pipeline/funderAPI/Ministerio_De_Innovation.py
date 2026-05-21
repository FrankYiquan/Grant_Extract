from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time


def get_MDI_grant(grantId):
     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
     driver.get("https://www.aei.gob.es/ayudas-concedidas/buscador-ayudas-concedidas")
     time.sleep(1)

     # Locate input field and submit search
     project_input = driver.find_element(By.ID, "edit-code")
     project_input.send_keys(grantId)

     # Handle cookie banner if it appears
     try:
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.agree-button.eu-cookie-compliance-secondary-button"))
        )
        accept_button.click()
     except:
        pass 
     
     submit_button = driver.find_element(By.ID, "edit-submit-grants-finder")
     submit_button.click()   

     #click the grant detail link
     year = None
     amount = None
     try:
        # Wait until all rows in the table body are loaded
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.table.table-hover.views-table.views-view-table.cols-11 tbody"))
        )

        for row in rows:
            year = row.find_element(By.CSS_SELECTOR, "td.views-field-year").text.strip()
            amount = row.find_element(By.CSS_SELECTOR, "td.views-field-amount").text.strip().replace(".",",")
        return{
            "amount": amount,
            "start_date": year,
            "currency": "Euro"
        }

     except Exception as e:
          print(e)
          driver.quit()
          return{
            "amount": None,
            "start_date": None,
            "currency": "Euro"
        }

result = get_MDI_grant("RYC2019-028510-I")
print(result)
         
    
# 308.600.182 => 308,600,182''
        


    
    


