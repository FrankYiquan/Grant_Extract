from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from funder_pipeline.utils.helper import escape_xml
from funder_pipeline.funderAPI.helper.schema_extract import get_grant_status_from_end_date, get_matched_funder_code
import re
from datetime import datetime

#TAGGS is the data system for funder with parent organization HHS (Health and Human Services)
def get_TAGGS_grant(projectId, funder_name):
    match = re.match(r'^(90[A-Z]{4}[0-9]{4})', projectId)

    if match:
        projectId = match.group(1)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = "https://taggs.hhs.gov/SearchAward"
    driver.get(url)
    time.sleep(2)

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"

    # Locate input field 
    wait = WebDriverWait(driver, 20)

    project_input = wait.until(
        EC.presence_of_element_located((By.ID, "tb_Keywords_I"))
    )
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

    hasData = True
    if rows[4].text == "No data to display":
        hasData = False

    # title is the same acroos all years and data is sorted by start date with the most recent one first
    if hasData:
        data = rows[-3].find_elements(By.TAG_NAME, "td")
        link = data[7].find_element(By.TAG_NAME, "a")

        grant_url = link.get_attribute("href")
        title = escape_xml(data[7].text)
        driver.get(grant_url)

        start_li = driver.find_element(
            By.XPATH,
            "//li[.//strong[contains(text(),'PERIOD OF PERFORMANCE START DATE')]]"
        )

        start_date_str = start_li.text.split(":")[-1].strip()

        startDate = datetime.strptime(
            start_date_str,
            "%m/%d/%Y"
        ).strftime("%Y-%m-%d")
                
        startDate = time.strftime("%Y-%m-%d", time.strptime(start_date_str, "%m/%d/%Y"))

        end_li = driver.find_element(
            By.XPATH,
            "//li[.//strong[contains(text(),'PERIOD OF PERFORMANCE END DATE')]]"
        )

        end_date_str = end_li.text.split(":")[-1].strip()

        endDate = datetime.strptime(
            end_date_str,
            "%m/%d/%Y"
        ).strftime("%Y-%m-%d")

        status = get_grant_status_from_end_date(endDate)

        grand_total_text = driver.find_element(
            By.XPATH,
            "//*[contains(text(),'Grand Total All Awards')]"
        ).text
        amount_fig = re.search(r"\$[\d,]+", grand_total_text).group()
        amount = float(amount_fig.replace("$", "").replace(",", ""))
            

    result = f"""<grant>
    <grantId>{projectId}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.USD</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""

    return result
        
        
print(get_TAGGS_grant("R01HD090103", "National Institute on Disability, Independent Living, and Rehabilitation Research"))