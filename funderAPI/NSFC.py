

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
from utils.helper import escape_xml


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

    found = True

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//p[contains(@class,'textEllipsis')]/a")
            )
        )
    except TimeoutException:
        found = False
        pass
    current_url = driver.current_url

    amount = None
    principal_investigator = None
    startDate = None
    endDate = None
    title = None
    status = "ACTIVE"
    grant_url = None
    funderCode = "41___NATIONAL_NATURAL_SCIENCE_FOUNDATION_OF_CHINA_(BEIJING)"

    if found:
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
            start_year_elem = driver.find_element(
                By.XPATH, "//div[contains(@class,'textEllipsis') and contains(@class,'el-col-5') and contains(text(),'批准年度')]"
            )
            
            start_match = re.search(r'(\d{4})', start_year_elem.text)

            if start_match:
                startDate = start_match.group(1)
                startDate = f"{startDate}-01-01"

        except :
            pass

        try:
            end_year_elem = driver.find_element(
                By.XPATH, "//div[contains(@class,'textEllipsis') and contains(@class,'el-col-6') and contains(text(),'结题年度')]"
            )
            
            end_match = re.search(r'(\d{4})', end_year_elem.text)

            if end_match:
                endDate = end_match.group(1)
        
        except :
            pass

        if endDate and int(endDate) < time.localtime().tm_year:
                status = "HISTORY"
        
        endDate = f"{endDate}-12-31"
    
        try:
            # Locate the <a> inside the p with class 'textEllipsis'
            title_elem = driver.find_element(
                By.XPATH,
                "//p[contains(@class,'textEllipsis')]/a"
            )
            title_text = title_elem.text  
            # Remove leading number and dot (like "1.") using regex
            title = re.sub(r'^\d+\.', '', title_text).strip()
            title = escape_xml(title)

        except Exception as e:
            pass

        # to get the grant url, we need to click the title, then js handle the redirection
        original_window = driver.current_window_handle

        # click using JS (more reliable)
        driver.execute_script("arguments[0].click();", title_elem)

        # wait for new window
        WebDriverWait(driver, 10).until(
            lambda d: len(d.window_handles) > 1
        )

        # switch to new window
        for handle in driver.window_handles:
            if handle != original_window:
                driver.switch_to.window(handle)
                break

        # now get the URL
        grant_url = driver.current_url

        driver.quit()


    result = f"""<grant>
    <grantId>{projectId}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.CNY</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""

    return result

print(get_nsfc_grant("71974204"))