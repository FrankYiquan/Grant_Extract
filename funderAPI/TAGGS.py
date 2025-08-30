from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time

#TAGGS is the data system for "National Institute on Disability, Independent Living, and Rehabilitation Research

def get_TAGGS_grant(projectId):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://taggs.hhs.gov/SearchAward")
    time.sleep(2)

    # Locate input field 
    project_input = driver.find_element(By.ID, "tb_Keywords_I")
    project_input.send_keys(projectId)

    time.sleep(2)
    
    # locate fiscal year dropdown and select "All"
    fy_input = driver.find_element(By.ID, "checkComboBox_I")
    fy_input.clear()
    
    time.sleep(2)
    
    # locate search button
    search_button = driver.find_element(By.ID, "btn_Search_I")
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(2)

    # traverse the results
    table = driver.find_element(By.ID, "GridView_DXMainTable")
    rows = table.find_elements(By.TAG_NAME, "tr")

    amount = driver.find_element(By.CLASS_NAME, "number").text.split("$")[-1].strip()
    start_date = None
    title = None
   
    # title is the same acroos all years and data is sorted by start date with the most recent one first
    if amount != "0":
        data = rows[-3].find_elements(By.TAG_NAME, "td")
        start_date = data[11].text
        title = data[7].text
    

    return {
        "title": title,
        "amount": amount,
        "start_date": start_date,
        "currency": "USD"
    }
        
        

print(get_TAGGS_grant("erfer"))