#this script is used to get information about National Sceience Fundation awards
import re
import requests


def clean_award_id(award_id):
    award_id = str(award_id).strip()
    match = re.search(r'\d+', award_id)
    return match.group() if match else None

def get_nsf_award(award_id):


    #normalize the award_id to ensure it is a string
    normalized_award_id = clean_award_id(award_id)
    if not normalized_award_id:
        print("Invalid award ID format.")
        return None
    url = f"http://api.nsf.gov/services/v1/awards/{normalized_award_id}.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Access the first award in the list
        award = data["response"]["award"][0]

        return {
            "startDate": award["startDate"],
            "amount": award["fundsObligatedAmt"]
        }

    except Exception as e:
        print(f"Error: {e}")
        return None
        
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


print(get_nsf_award(1919565))