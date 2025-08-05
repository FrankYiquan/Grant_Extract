import requests

def extract_ANDLR_grant(projectId, datasetId="20-ans-de-l-anr-liste-projets-plan-d-action_2005-a-2024"):
    url = f"https://dataanr.opendatasoft.com/api/explore/v2.1/catalog/datasets/{datasetId}/records?where=code_projet_anr='{projectId}'"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        startDate = None
        amount = None

        if data.get('total_count') > 0:
            grant = data.get('results')[0]
            startDate = grant.get('edition')
            amount = grant.get('aide_allouee_projet')

        return {
            "startDate": startDate,
            "amount": amount,
            "currency": "Euro"
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "startDate": None,
            "amount": None,
            "currency": "Euro"
        }


# print(extract_ANDLR_grant('ANR-20-CE31-0013'))