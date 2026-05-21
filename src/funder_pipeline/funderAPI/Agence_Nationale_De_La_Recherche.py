import requests
from src.funder_pipeline.utils.helper import escape_xml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import date
import re
from funder_pipeline.utils.helper import escape_xml
from funder_pipeline.funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)

month_map = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12
}

# Add a certain number of months to a date, handling year rollover
def add_months(start_date, months):
    year = start_date.year + (start_date.month - 1 + months) // 12
    month = (start_date.month - 1 + months) % 12 + 1
    return date(year, month, 1)

def normalize_id(award_id: str) -> str:
    if award_id.startswith("NR"):
        award_id = award_id.replace("NR", "ANR")

    parts = award_id.split('-')
    
    if len(parts) <= 4:  # 3 or fewer dashes
        return award_id
    
    return '-'.join(parts[:4])  # keep up to 3rd dash

def extract_ANDLR_grant(award_id: str, funder_name: str):
    normalize_award_id = normalize_id(award_id)
    url = f"https://dataanr.opendatasoft.com/api/explore/v2.1/catalog/datasets/20-ans-de-l-anr-liste-projets-plan-d-action_2005-a-2024/records?where=code_projet_anr='{normalize_award_id}'&limit=1"

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    awardID = normalize_award_id
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"

    # first, look for general dataset where there is only title and link provided
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("total_count", 0) > 0:
            grant = data["results"][0]

            awardID = grant.get("code_projet_anr")

            title = grant.get("projet_titre_anglais")
            if title is None:
                title = grant.get("projet_titre_francais")
            title = escape_xml(title)
            
            grant_url = grant.get("lien")

            startYear = int(grant.get("edition"))
            startDate = date(startYear, 1, 1) if startYear else None
    
        # following the link, web scrape the amount, startDate, endDate
        if grant_url:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get(grant_url)
            time.sleep(1)

            # the info is located within <strong> tags
            # we get all the strong tags
            try:
                strongs = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//section[contains(@class,'block-info')]//strong")
                    )
                )
            except TimeoutException:
                strongs = []
                pass

            # filter the useful <strong> tags
            for el in strongs:
                text = el.text.strip().lower()

                # amount
                if any(k in text for k in ["aide", "montant"]) and "anr" in text:
                    m = re.search(r'\d[\d\s\xa0]*', text)
                    if m:
                        amount = int(
                            m.group()
                            .replace("\xa0", "")
                            .replace(" ", "")
                        )

                # DATE + DURATION
                elif any(k in text for k in ["début", "duree", "durée"]):

                    m = re.search(
                        r'(?:'
                            r'(?:(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+)?'
                            r'(\d{4})'
                        r')?'
                        r'[^0-9]*'
                        r'(\d+)\s*(?:mois|months?)',
                        text,
                        re.IGNORECASE
                    )

                    duration_months = None

                    if m:
                        month_str, year, duration = m.groups()
                        print(f"Extracted from text: month={month_str}, year={year}, duration={duration}")

                        # handle missing month 
                        month = month_map.get(month_str, None) if month_str else None
                        year = int(year) if year else None
                        duration_months = int(duration) if duration else None

                        if year and month:
                            # build start date (always day = 01)
                            startDate = date(year, month, 1)

                    if startDate and duration_months:
                        #  compute end date 
                        endDate = add_months(startDate, duration_months)

                        if endDate < date.today():
                            status = "HISTORY"    
    result = f"""<grant>
    <grantId>{awardID}</grantId>
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
            

# print(extract_ANDLR_grant('NR-21-CE49-0008-01', "Agence Nationale de la Recherche"))
