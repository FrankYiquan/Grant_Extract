
#this script fetches NIH award information using the NIH Reporter API
import requests
import csv
import re
from datetime import datetime, date

# Lists of activity codes and IC codes
activity_codes = [
    "C06", "D43", "D71", "DP1", "DP2", "DP3", "DP4", "DP5", "DP7", "F05",
    "F30", "F31", "F32", "F33", "F37", "F38", "G07", "G08", "G11", "G12",
    "G13", "G20", "K01", "K02", "K05", "K07", "P2C", "P30", "P40", "P41",
    "P42", "P50", "P51", "P60", "PL1", "PM1", "PN1", "PN2", "R00", "R01",
    "R03", "R13", "R15", "R16", "R18", "R21", "R24", "R25", "R28", "R2F",
    "R30", "R33", "R34", "R35", "R36", "R37", "R50", "R55", "R56", "R61",
    "RC1", "RC2", "RC3", "RL2", "RM1", "RP1", "RS1", "S06", "S07", "S10",
    "S11", "S15", "S21", "S22", "SB1", "SC1", "SC2", "SC3", "SI2", "T01",
    "T02", "T03", "T06", "T14", "T15", "T32", "T34", "T35", "T36", "T37",
    "T42", "T90", "R90", "TU2", "U01", "U10", "U13", "U18", "U19", "U24",
    "U2C", "U2R", "U34", "U41", "U42", "U43", "U44"
]

ic_codes = [
    "TW", "TR", "AT", "CA", "EY", "HG", "HL", "AG", "AA", "AI",
    "AR", "EB", "HD", "DA", "DC", "DE", "DK", "ES", "GM", "MH",
    "MD", "NS", "NR", "LM", "OD", "RR"
]

def standardize_nih_award_id(raw_id):
    """
    Standardize NIH award ID into format:
    <activity_code><IC_code><6-digit serial_number>[-YY]
    Ignores any prefix before the activity code and handles spaces or dashes.
    """
    # Normalize string: remove spaces, replace Unicode dashes with "-"
    raw_id = re.sub(r"[‐–—]", "-", raw_id)
    # raw_id = re.sub(r"\s+", "", raw_id)
    # raw_id = raw_id.replace("_", "")
    raw_id = raw_id.upper()

    # Find the first occurrence of a 6-digit number to limit search scope
    six_digit = re.search(r'\d{6}', raw_id)
    if six_digit:
        digit_start_index = six_digit.start()
    else:
        digit_start_index = len(raw_id)
    
    # Search for activity code anywhere in the string
    matches = [(code, raw_id.find(code)) for code in activity_codes if code in raw_id]
    if matches and digit_start_index > min(matches, key=lambda x: x[1])[1] + 3:
        activity_code, start_idx = min(matches, key=lambda x: x[1])
        
        # Keep only substring starting from that activity code
        remaining = raw_id[start_idx + len(activity_code):]
    else:
        activity_code = ""
        remaining = raw_id
         
    # Extract IC code
    ic_code = next((code for code in ic_codes if code in remaining), None)
    if not ic_code:
        m = re.search(r'\d{6}', remaining)
        return m.group(0) if m else "error"
    
    remaining = remaining[len(ic_code):]

    # Extract serial number (first 1-6 digits)
    serial_match = re.search(r'\d{4,6}', remaining)
    if not serial_match:
        return "error"
    serial_number = serial_match.group().zfill(6)

    remaining = remaining[serial_match.end():]
    
    # Extract optional -YY (support year)
    year_match = re.search(r'\d{2}', remaining)
    year_suffix = "-" + year_match.group() if year_match else ""
    
    standardized_code = f"{activity_code}{ic_code}{serial_number}{year_suffix}"
    return standardized_code

def get_award_from_NIH(award_id: str, funder_name: str):
    
    #normalize it to prevent case like U19-AG051426 => U19AG051426
    original_award_id = award_id
    award_id = standardize_nih_award_id(award_id)
    url = "https://api.reporter.nih.gov/v2/projects/search"
    params = {
        "criteria": {
            "project_nums": [award_id]
        },
        "format": "json",
        "sort_field": "fiscal_year",
        "sort_order": "desc"
    }

    response = requests.post(url, json=params)

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = None
    status = "ACTIVE"

    if response.status_code == 200:
        data = response.json()
        hits = data.get('meta').get('total')
        
        if hits > 0:
            amount = sum(grant.get('award_amount', 0) or 0 for grant in data['results'])
            # for grant in data['results']:
            #     print(f"Year: {grant['fiscal_year']}, Award Amount: {grant['award_amount']}")
            project_start = data['results'][0].get('project_start_date')
            project_end = data['results'][0].get('project_end_date')
            if project_start:
                startDate = project_start.split('T')[0]
            else:
                startDate = None 

            if project_end:
                endDate = project_end.split('T')[0]
                target_date = datetime.strptime(endDate, "%Y-%m-%d").date()
                today = date.today()
                if target_date < today:
                    status = "HISTORY"
            else:
                endDate = None
            
            principal_investigator = data['results'][0]['principal_investigators'][0]['full_name']
            grant_url = data.get('meta').get("properties").get("URL")
            title = data['results'][0]['project_title']
            award_id = data.get('results')[0].get('project_serial_num')
        else:
            print(f"No results for original award ID {original_award_id}, normalized award ID {award_id}")
            award_id = original_award_id

        # match with funder_41Code.csv
        with open('./resources/funder_41Code.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['unique_funder'] == funder_name:
                    funderCode = row['matched_funder_code']
                    break

        result = f"""<grant>
    <grantId>{award_id}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
     <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
        return result
        

#list of NIH institutes
nih_institutes = [
    "Division of Intramural Research, National Institute of Allergy and Infectious Diseases",
    "Division of Microbiology and Infectious Diseases, National Institute of Allergy and Infectious Diseases",
    "Eunice Kennedy Shriver National Institute of Child Health and Human Development",
    "Foundation for the National Institutes of Health",
    "National Heart, Lung, and Blood Institute",
    "National Institute of Allergy and Infectious Diseases",
    "National Institute of Arthritis and Musculoskeletal and Skin Diseases",
    "National Institute of Biomedical Imaging and Bioengineering",
    "National Institute of Child Health and Human Development",
    "National Institute of Diabetes and Digestive and Kidney Diseases",
    "National Institute of Environmental Health Sciences",
    "National Institute of General Medical Sciences",
    "National Institute of Mental Health",
    "National Institute of Neurological Disorders and Stroke",
    "National Institute of Standards and Technology",
    "National Institute on Aging",
    "National Institute on Alcohol Abuse and Alcoholism",
    "National Institute on Drug Abuse",
    "National Institutes of Health",
    "Office of Extramural Research, National Institutes of Health",
    "National Eye Institute",
    "U.S. National Library of Medicine",
    "National Center for Complementary and Integrative Health",
    "National Institute on Deafness and Other Communication Disorders",
    "National Cancer Institute"
]

#check if a funder name is a NIH institute
def check_nih_funder(funder_name: str):
    return any(nih_institute.lower() in funder_name.lower() for nih_institute in nih_institutes)

# get a list of unique funders that are NIH institutes
def filter_nih_from_unique_funders():
    import json
    with open("unique_funders.json", "r") as f:
        unique_funders = json.load(f)

    nih_funders = [funder for funder in unique_funders if check_nih_funder(funder)]
    
    with open("nih_funders.json", "w") as f:
        json.dump(nih_funders, f, indent=2)
    
    print(f"Filtered {len(nih_funders)} NIH funders from {len(unique_funders)} unique funders.")



# award_id= "GM111978"
# funder_name="National Institutes of Health"
# print(get_award_from_NIH(award_id, funder_name))


