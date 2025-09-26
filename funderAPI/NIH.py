#this script fetches NIH award information using the NIH Reporter API
import requests
import csv

def get_award_from_NIH(award_id: str, funder_name: str):

    #normalize it to prevent case like U19-AG051426 => U19AG051426
    award_id = award_id.replace("-", "")
    award_id = award_id.split("NIH")[-1].strip() if "NIH" in award_id else award_id.strip()
    
    url = "https://api.reporter.nih.gov/v2/projects/search"
    params = {
        "criteria": {
            "project_nums": [award_id]
        },
        "format": "json",
        "sort_field":"fiscal_year",
        "sort_order":"desc"
    }

    response = requests.post(url, json=params)


    amount = None
    startDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = None



    if response.status_code == 200:
        data = response.json()
        hits = data.get('meta').get('total')
        
        # traverse the json result
        if hits > 0:
            amount= sum(grant['award_amount'] for grant in data['results'])
            for grant in data['results']:
                print(f"Year: {grant['fiscal_year']}, Award Amount: {grant['award_amount']}")
            startDate = data['results'][0]['project_start_date'].split('T')[0]  # Strips the time part
            principal_investigator = data['results'][0]['principal_investigators'][0]['full_name']
            grant_url =  data.get('meta').get("properties").get("URL")
            title = data.get('results')[0].get('project_title')
            award_id = data.get('results')[0].get('project_serial_num')
           
        else:
            print(f"Error fetching data for award ID {award_id}: {response.status_code}")

        # match with the 41 code 
        with open('./resources/funder_41Code.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)  

            # Iterate through rows
            for row in reader:
                if row['unique_funder'] == funder_name:
                    funderCode = row['matched_funder_code']
                    break

                

        
        return {
            "grantId": award_id,
            "grantName": title,
            "funderCode": funderCode,
            "amount": amount,
            "startDate": startDate,
            "grantURL": grant_url,
        }
        

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
    "National Institute of Mental Health and Neurosciences",
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

#filter_nih_from_unique_funders()

# # Example usage
award_id = "R35GM147556"
funder_name = "National Institute of General Medical Sciences"

# award_id = "NIH CA142746"

# award_id = "NIH CA142746"
# funder_name = "National Institutes of Health"

award_id= "F32 NS112453"
funderName="National Institutes of Health"
print(get_award_from_NIH(award_id, funder_name))


