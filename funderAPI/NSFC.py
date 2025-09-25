

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.keys import Keys
import re



def get_nsfc_grant(projectId):
    projectId = projectId.replace(" ", "") if " " in projectId else projectId
    projectId = projectId.split("NSFC-")[-1] if "NSFC-" in projectId else projectId
  
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("http://kd.nsfc.cn/finalProjectInit")
    time.sleep(1)

    project_input = driver.find_element(
        By.XPATH, "//input[contains(@class,'el-input__inner')]"
    )

    project_input.send_keys(projectId)
    project_input.send_keys(Keys.ENTER)

    time.sleep(3)

    amount = None
    principal_investigator = None
    start_date = None
    title = None

    try:
        # Locate the <a> inside the div with class 'textEllipsis el-col el-col-7'
        person_elem = driver.find_element(
            By.XPATH,
            "//div[contains(@class,'textEllipsis') and contains(@class,'el-col-7')]/a"
        )

        principal_investigator  = person_elem.text
    except:
        pass


    try:
    # Locate the div with el-col-6 (fund amount)
        fund_elem = driver.find_element(
        By.XPATH, "//div[contains(@class,'textEllipsis') and contains(@class,'el-col-6') and contains(text(),'资助经费')]"
    )
        fund_amount = fund_elem.text

        match = re.search(r'([\d.]+)', fund_elem.text)
        if match:
            amount = match.group(1)
            amount = float(amount) * 10000 if "万" in fund_amount else amount
    except :
        pass
    try:
        # Locate the div with el-col-5 (start/approved year)
        year_elem = driver.find_element(
            By.XPATH, "//div[contains(@class,'textEllipsis') and contains(@class,'el-col-5') and contains(text(),'批准年度')]"
        )
        start_year = year_elem.text 
        match = re.search(r'(\d{4})', year_elem.text)
        if match:
            start_date = match.group(1)
    except :
        pass

   
    try:
        # Locate the <a> inside the p with class 'textEllipsis'
        title_elem = driver.find_element(
            By.XPATH,
            "//p[contains(@class,'textEllipsis')]/a"
        )
        title_text = title_elem.text  
        # Remove leading number and dot (like "1.") using regex
        title = re.sub(r'^\d+\.', '', title_text).strip()

        
    except Exception as e:
       pass

    return {
        "title": title,
        "amount": amount,
        "start_date": start_date,
        "principal_investigator": principal_investigator,
        "currency": "CNY"
    }

print(get_nsfc_grant("71974204"))

