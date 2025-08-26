#this script fetches NIH award information using the NIH Reporter API
import requests
def get_award_from_NIH(award_id: str):

    #normalize it to prevent case like U19-AG051426 => U19AG051426
    award_id = award_id.replace("-", "")
    
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
    if response.status_code == 200 and response != None:
        data = response.json()
        award_amount = sum(grant['award_amount'] for grant in data['results'])
        for grant in data['results']:
            print(f"Year: {grant['fiscal_year']}, Award Amount: {grant['award_amount']}")
        project_start_date = data['results'][0]['project_start_date'].split('T')[0]  # Strips the time part
        principal_investigator = data['results'][0]['principal_investigators'][0]['full_name']
        return {
            "award_amount": award_amount,
            "project_start_date": project_start_date,
            "principal_investigator": principal_investigator
        }
    else:
        print(f"Error fetching data for award ID {award_id}: {response.status_code}")
        return None

#list of NIH institutes
nih_institutes = [
    "National Cancer Institute",
    "National Institute of Allergy and Infectious Diseases",
    "National Institute of Arthritis and Musculoskeletal and Skin Diseases",
    "National Institute of Child Health and Human Development",
    "National Institute on Drug Abuse",
    "National Institute of Diabetes and Digestive and Kidney Diseases",
    "National Institute of Environmental Health Sciences",
    "National Institute of General Medical Sciences",
    "National Heart, Lung, and Blood Institute",
    "National Institute of Mental Health",
    "National Institute of Neurological Disorders and Stroke",
    "National Institute of Nursing Research",
    "National Institute on Aging",
    "National Institute of Deafness and Other Communication Disorders",
    "National Institute of Dental and Craniofacial Research",
    "National Institute of Biomedical Imaging and Bioengineering",
    "National Institute of Minority Health and Health Disparities",
    "National Institute of Mental Health",
    "National Library of Medicine",
    "National Institute of Occupational Safety and Health ",
    "National Institute on Alcohol Abuse and Alcoholism",
    "National Institute of Human Genome Research",
    "National Institute of Standards and Technology",
    "National Institute of Advanced Technology",
    "National Institute for Environmental Health Sciences",
    "National Institute of Nursing Research",
    "National Institute on Aging and Aging",
    "National Institutes of Health"

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
# award_id = "R35GM147556"

# award_id = "75N91019D00024"
# print(get_award_from_NIH(award_id))


