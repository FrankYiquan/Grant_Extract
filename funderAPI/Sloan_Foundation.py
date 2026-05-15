# protected by cloudfare

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import random
from utils.helper import escape_xml
from funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)
import time

def get_ARC_grant(projectId, funder_name):

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"

    # FG started id is fellowship - fixed for two years
    if projectId.startswith("FG") or projectId.startswith("fg"):
        startYear = projectId.split('-')[1] if '-' in projectId else None
        fellowship_amount = get_fellowship_amount(int(startYear)) # get the fellowship amount based on the start year

        amount = fellowship_amount,
        startDate = get_start_end_date(int(startYear), True)
        endDate = get_start_end_date(int(startYear), False)
        status = get_grant_status_from_end_date(endDate)

    else: 
        options = Options()

        # Use real browser window
        options.add_argument("--start-maximized")

        # Keep persistent session
        options.add_argument("user-data-dir=./chrome_profile")

        # Reduce automation fingerprints
        options.add_experimental_option(
            "excludeSwitches",
            ["enable-automation"]
        )
        options.add_experimental_option(
            "useAutomationExtension",
            False
        )

        # Realistic browser identity
        options.add_argument(
            "user-agent=Mozilla/5.0 "
            "(Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        # Hide webdriver property
        driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """)

        wait = WebDriverWait(driver, 15)

        projectId = "G-2024-12345"

        driver.get("https://sloan.org/grants-database")

        # Random human-like pause
        time.sleep(random.uniform(2.5, 5))

        # Wait for search input
        search_input = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div.database-search input[name='keywords']"
            ))
        )

        # Type slowly like human
        for ch in projectId:
            search_input.send_keys(ch)
            time.sleep(random.uniform(0.08, 0.18))

        time.sleep(random.uniform(0.5, 1.5))

        search_input.send_keys(Keys.ENTER)

        # Wait for results
        wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "ul.data-list > li"
            ))
        )

        time.sleep(random.uniform(2, 4))

        try:
            accept_btn = wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "button.gdpr-banner__button--opt-in"
                ))
            )

            time.sleep(random.uniform(1, 2))

            accept_btn.click()

            time.sleep(random.uniform(1, 2))

        except:
            print("Cookie banner not found")


        grants = driver.find_elements(
            By.CSS_SELECTOR,
            "ul.data-list > li"
        )

        if grants:
            grant = grants[0]

            amount_text = grant.find_element(
                By.CSS_SELECTOR,
                "div.amount"
            ).text

            amount = (
                amount_text
                .replace("amount:", "")
                .replace("$", "")
                .replace(",", "")
                .strip()
            )

            startYear = grant.find_element(
                By.CSS_SELECTOR,
                "div.year"
            ).text.strip()

            title = grant.find_element(
                By.CSS_SELECTOR,
                "div.summary p"
            ).text.strip()
            title = escape_xml(title)

            link = grant.find_element(
                By.CSS_SELECTOR,
                "div.summary a.permalink"
            )

            grant_url = link.get_attribute("href")

            print({
                "amount": amount,
                "startYear": startYear,
                "title": title,
                "grant_url": grant_url
            })

        driver.quit()
      

        
    result = f"""<grant>
    <grantId>{projectId}</grantId>
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
        
   
# get the fellowship amount based on the start year
def get_fellowship_amount(fellowship_startDate):
    if fellowship_startDate > 2020:
        fellowship_amount = 75000
    elif 2010 <= fellowship_startDate <= 2020:
        fellowship_amount = 60000
    else:
        fellowship_amount = None 
    return fellowship_amount

def get_start_end_date(year, start):
    if not year:
        return None
    elif start:
        return f"{year}-09-15"
    else:
        return f"{year+2}-09-14"

    


print(get_ARC_grant("G-2017-9685", "Alfred P. Sloan Foundation"))


# print(get_ARC_grant("FG-2010-18328"))
        