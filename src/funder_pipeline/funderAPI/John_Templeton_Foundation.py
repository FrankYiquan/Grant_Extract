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

def clean_amount(amount_text):
    """
    '$2,450,000' -> '2450000'
    """

    if not amount_text:
        return None

    amount = re.sub(r"[^\d]", "", amount_text)

    return amount if amount else None


def extract_start_date(year_text):
    """
    '2024' -> '2024-01-01'
    """

    if not year_text:
        return None

    year_match = re.search(r"\d{4}", year_text)

    if year_match:
        return f"{year_match.group()}-01-01"

    return None


def get_templeton_grant(award_id, funder_name):

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = "https://www.templeton.org/grants/grant-database"
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

    wait = WebDriverWait(driver, 20)

    # accept cookie
    cookie_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button.btn.btn-desktop")
    )
)

    cookie_btn.click()

    # locate input and input award id
    search_box =  wait.until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "#grants-table_filter input"
        ))
    )
    search_box.send_keys(award_id)

    time.sleep(1)

    first_row = driver.find_element(
        By.CSS_SELECTOR,
        "#grants-table tbody tr"
    )

    # awards found
    if "No matching records found" not in first_row.text:
        cols = first_row.find_elements(By.TAG_NAME, "td")
        
        award_id = cols[1].text
        title = escape_xml(cols[2].text)
        amount = clean_amount(cols[5].text)
        # principal_investigator = cols[3].text

        grant_url = cols[2].find_element(
            By.TAG_NAME, "a"
        ).get_attribute("href")

        # visist detail project page
        driver.get(grant_url)

        date_text = driver.find_element(
            By.CSS_SELECTOR,
            ".topic-tag"
        ).text.strip()

        # start/end Date locate on the top left corner
        start_str, end_str = date_text.split(" - ")

        startDate = datetime.strptime(start_str, "%B %Y").strftime("%Y-%m-01")
        endDate = datetime.strptime(end_str, "%B %Y").strftime("%Y-%m-01")

    result = f"""<grant>
    <grantId>{award_id}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.usd</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""

    return result



    

    



result = get_templeton_grant("61075", "John Templeton Foundation") 
print(result)  