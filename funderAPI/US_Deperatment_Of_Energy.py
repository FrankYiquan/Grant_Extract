import re
import requests


def get_energy_award(award_id):
    # Normalize the award_id to get the required part

    award_id = re.search(r"00(\d+)", award_id).group(0)


    url = f"https://api.usaspending.gov/api/v2/awards/{award_id}/"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return {
            "startDate": data["date_signed"],
            "amount": data["total_obligation"]
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

print(get_energy_award("DE-SC0022102")  )

