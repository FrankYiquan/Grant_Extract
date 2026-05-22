from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from funder_pipeline.utils.helper import escape_xml
from funder_pipeline.funderAPI.helper.schema_extract import (
    get_matched_funder_code,
)



def get_MDI_grant(award_id, funder_name):
     
    award_id = award_id.replace(",", "") if "," in award_id else award_id
    award_id =  max(award_id.split(), key=len)

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"

    if len(award_id) > 8:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://www.aei.gob.es/ayudas-concedidas/buscador-ayudas-concedidas")
        time.sleep(1)

        # Locate input field and submit search
        project_input = driver.find_element(By.ID, "edit-code")
        project_input.send_keys(award_id)

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

        try:
        # Wait until all rows in the table body are loaded
            rows = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.table.table-hover.views-table.views-view-table.cols-11 tbody"))
            )

            amount_sum = 0
            earliest_year = float('inf')
            print(len(rows))
            for row in rows:
                year = int(
                    row.find_element(
                        By.CSS_SELECTOR,
                        "td.views-field-year"
                    ).text.strip()
                )

                earliest_year = min(earliest_year, year)

                amount_text = (
                    row.find_element(
                        By.CSS_SELECTOR,
                        "td.views-field-amount"
                    )
                    .text.strip()
                    .replace(",", "")
                    .replace(".", "")
                )

                amount_sum += int(amount_text)

                if not title:
                    title = escape_xml(
                        row.find_element(
                            By.CSS_SELECTOR,
                            "td.views-field-title"
                        ).text.strip()
                    )
            amount = amount_sum if amount_sum > 0 else None
            startDate = f"{earliest_year}-01-01" if earliest_year != float('inf') else None
            grant_url = driver.current_url

        except Exception as e:
            print(e)
    
    result = f"""<grant>
    <grantId>{award_id}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.eur</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""

    return result

# result = get_MDI_grant("RYC2019-028510-I", "Ministerio de Ciencia e Innovación")
# print(result)    






