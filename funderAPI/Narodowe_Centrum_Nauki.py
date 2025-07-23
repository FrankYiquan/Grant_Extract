from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_NCN_grant(grantId):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://projekty.ncn.gov.pl")
    time.sleep(2)

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
        driver.quit()
        return {
            "amount": None,
            "currency": None,
            "start_date": None,
            "error": f"No results found for grantId: {grantId}"
        }

    # If grant found, proceed
    if results:
        href = results[0].get_attribute("href")
        driver.get(href)

        try:
            project_info_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.strona"))
            )
        except TimeoutException:
            driver.quit()
            return {
                "amount": None,
                "currency": None,
                "start_date": None,
                "error": "cannot load grant detail page"
            }

        # extract amount and start date
        divs = driver.find_elements(By.CSS_SELECTOR, "div.strona")

        target_div = None
        for div in divs:
            if "Przyznana kwota" in div.text:
                target_div = div
                break

        amount = None
        start_date = None
        currency = None

        if target_div:
            lines = target_div.text.split("\n")

            for line in lines:
                if "Przyznana kwota" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        amount_str = parts[1].strip()
                        amount_parts = amount_str.split()
                        currency = amount_parts[-1]
                        number_str = "".join(amount_parts[:-1])
                        amount = int(number_str)
                elif "Rozpoczęcie projektu" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        start_date = parts[1].strip()

        driver.quit()
        return {
            "amount": amount,
            "currency": currency,
            "start_date": start_date
        }

    driver.quit()
    return {
        "amount": None,
        "currency": None,
        "start_date": None,
        "error": "found grant but no amount or startdate"
    }

print(get_NCN_grant("2rhi2r3h"))