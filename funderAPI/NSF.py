#this script is used to get information about National Sceience Fundation awards
import re
import requests
from datetime import datetime, date


def clean_award_id(award_id):
    text = str(award_id).strip()

    # Find all digit sequences in the string
    digit_groups = re.findall(r'\d+', text)

    if not digit_groups:
        return []

    # If the string contains more than one award code (detected by prefix letters)
    # Example: "DMR-1809762 CBET-1916877"
    codes = re.findall(r'[A-Za-z]+[- ]*\d+', text)
    if len(codes) > 1:
        # Multiple award codes → return each full ID separately
        return [
                digits 
                for code in codes
                for digits in [re.findall(r'\d+', code)[0]]
                if len(digits) > 3
            ]   

    # Otherwise: one award code → combine digit pieces
    return ["".join(digit_groups)]

def get_award_from_NSF(award_id):


    #normalize the award_id to ensure it is a string
    normalized_award_id = clean_award_id(award_id)[0]
   
    url = f"http://api.nsf.gov/services/v1/awards/{normalized_award_id}.json"

    response = requests.get(url)
    data = response.json()

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = "41___NATIONAL_SCIENCE_FOUNDATION_(ALEXANDRIA)"
    status = "ACTIVE"

    if response.status_code == 200 and data.get("response", {}).get("metadata", {}).get("totalCount", 0) > 0:
        # Access the first award in the list
        award = data["response"]["award"][0]
        amount = award.get("fundsObligatedAmt")

        project_start = award.get("startDate")
        if project_start:
            startDate = datetime.strptime(project_start, "%m/%d/%Y").strftime("%Y-%m-%d")

        project_end = award.get("expDate")
        if project_end:
            endDate = datetime.strptime(project_end, "%m/%d/%Y").strftime("%Y-%m-%d")
            end_date = datetime.strptime(project_end, "%m/%d/%Y").date()
            if end_date < datetime.now().date():
                status = "HISTORY"
        
        title = award.get("title")
        award_id = award.get("id")
        grant_url = "https://www.nsf.gov/awardsearch/show-award?AWD_ID=" + award_id

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

    
        
NSF_ORGANIZATIONS = [
    "National Science Foundation",
    "NSF",
    "Directorate for Biological Sciences",
    "Division of Biological Infrastructure",
    "Division of Environmental Biology",
    "Division of Integrative Organismal Systems",
    "Division of Molecular and Cellular Biosciences",
    "Division of Organismal Biology and Ecology",
    "Division of Symbiosis, Ecological and Evolutionary Biology",

    "Directorate for Computer and Information Science and Engineering",
    "Division of Computing and Communication Foundations",
    "Division of Computer and Network Systems",
    "Division of Information and Intelligent Systems",
    "Division of Data and Information Systems",
    "Division of Cyber-Physical Systems",

    "Directorate for Engineering",
    "Division of Chemical, Bioengineering, Environmental, and Transport Systems",
    "Division of Civil, Mechanical, and Manufacturing Innovation",
    "Division of Electrical, Communications, and Cyber Systems",
    "Division of Industrial Innovation and Partnerships",
    "Division of Materials Research",
    "Division of Electrical, Optical and Magnetic Materials",

    "Directorate for Geosciences",
    "Division of Atmospheric and Geospace Sciences",
    "Division of Earth Sciences",
    "Division of Ocean Sciences",
    "Division of Polar Programs",
    "Division of Geo-science Diversity and Inclusion",

    "Directorate for Mathematical and Physical Sciences",
    "Division of Astronomical Sciences",
    "Division of Chemistry",
    "Division of Mathematical Sciences",
    "Division of Physics",

    "Directorate for Social, Behavioral and Economic Sciences",
    "Division of Behavioral and Cognitive Sciences",
    "Division of Social and Economic Sciences",
    "Division of Research on Learning in Formal and Informal Settings",

    "Directorate for Education and Human Resources",
    "Division of Graduate Education",
    "Division of Human Resource Development",
    "Division of Undergraduate Education",

    "Directorate for Innovation and Industry",
    "Division of Small Business Innovation Research",

    "Directorate for International Science and Engineering",
    "Office of Advanced Cyberinfrastructure",
    "Advanced Cyberinfrastructure Division",
    "Antarctic Sciences Program",
    "Arctic Sciences Program"
]

def check_nsf_funder(funder: str) -> bool:
    funder_lower = funder.lower()
    return any(org.lower() in funder_lower for org in NSF_ORGANIZATIONS)


# get a list of unique funders that are NIH institutes
def filter_nih_from_unique_funders():
    import json
    with open("unique_funders.json", "r") as f:
        unique_funders = json.load(f)

    nsf_funders = [funder for funder in unique_funders if check_nsf_funder(funder)]
    
    with open("nsf_funders.json", "w") as f:
        json.dump(nsf_funders, f, indent=2)
    
    print(f"Filtered {len(nsf_funders)} NSF funders from {len(unique_funders)} unique funders.")


#filter_nih_from_unique_funders()
# print(check_nsf_funder("United States - Israel Binational Science Foundation"))  # Example usage

# # Example usage
# info = get_award_info("")
# print(info)


# print(get_award_from_NSF("1144152"))

# award_id = "DMR-1809762 CBET-1916877 CMMT-2026834 BSF- 2016188"
# result = clean_award_id(award_id)
# print(result)