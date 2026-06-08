from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
import time
from funder_pipeline.handlers.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)
from funder_pipeline.utils.web_scrap import get_driver

def extract_NCN_award(grantId, funder_name):
    with get_driver() as driver:
        driver.get("https://projekty.ncn.gov.pl")
        time.sleep(2)

        amount = None
        startDate = None
        endDate = None
        principal_investigator = None
        grant_url = None
        title = None
        funderCode = get_matched_funder_code(funder_name)
        status = "ACTIVE"

        # Locate input field and submit search
        project_input = driver.find_element(By.ID, "idprojekt")
        project_input.send_keys(grantId)
        submit_button = driver.find_element(By.ID, "wyszukaj")
        submit_button.click()

        # Try locating grant result(pick first one)
        try:
            results = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#wynikiwyszukiwarki ol li p.row1 a"))
            )
        except TimeoutException:
            pass

        # If grant found, proceed
        if results:
            href = results[0].get_attribute("href")

            driver.get(href)

            grant_url = href

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.important")
                    )
                )

            except TimeoutException:
                pass
            
            # ----------------------------
            # grantId
            # ----------------------------
            grantId = (
                driver.find_element(
                    By.CSS_SELECTOR,
                    "div.important p.row2"
                )
                .text.strip()
            )

            # ----------------------------
            # title
            # ----------------------------
            title = (
                driver.find_element(
                    By.CSS_SELECTOR,
                    "div.important h2"
                )
                .text.strip()
            )

            # ----------------------------
            # find all info blocks
            # ----------------------------
            divs = driver.find_elements(By.CSS_SELECTOR, "div.strona")

            for div in divs:
                text = div.text
                # ----------------------------
                # amount
                # ----------------------------
                if "Przyznana kwota" in text:
                    match = re.search(
                        r"Przyznana kwota.*?:\s*([\d\s]+)",
                        text
                    )

                    if match:
                        amount = re.sub(r"\D", "", match.group(1))

                # ----------------------------
                # start date
                # ----------------------------
                start_match = re.search(
                    r"Rozpoczęcie projektu.*?:\s*([\d-]+)",
                    text
                )

                if start_match:
                    startDate = start_match.group(1)

                # ----------------------------
                # end date
                # ----------------------------
                end_match = re.search(
                    r"Zakończenie projektu.*?:\s*([\d-]+)",
                    text
                )

                if end_match:
                    endDate = end_match.group(1)
                    status = get_grant_status_from_end_date(endDate)

    result = f"""<grant>
    <grantId>{grantId}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.clp</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
    return result    

    
# print(extract_NCN_award("UMO-2023/49/B/ST2/04085", "Narodowe Centrum Nauki"))