from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


def extract_awards(awards, start_year, end_year, funder_id, funder_name):
    successful_awards = []
    failed_awards = []
    error_awards = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_award = {
            executor.submit(
                award["handler"],
                award["award"],
                award["final_funder_name"]
            ): award
            for award in awards
        }

        for future in future_to_award:
            award = future_to_award[future]

            try:
                xml_result = future.result()

                if not xml_result:
                    failed_awards.append({
                        "award": award,
                        "reason": "handler returned None"
                    })
                    continue

                amount_match = re.search(
                    r"<amount>(.*?)</amount>",
                    xml_result,
                    re.DOTALL
                )

                amount = amount_match.group(1).strip() if amount_match else None

                if amount in (None, "", "None"):
                    failed_awards.append({
                        "award": award,
                        "reason": "amount is None"
                    })
                else:
                    successful_awards.append(xml_result)

            except Exception as e:
                error_awards.append({
                    "award": award,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })

    
    import_awards_output_dir = (
        Path("outputs")
        / "import_awards"
        / f"{funder_name}_{start_year}_{end_year}_imported_awards.csv"
    )

    xml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<grants xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="schema1.xsd">
'''
    xml_footer = '</grants>'

    
    with open(import_awards_output_dir, 'w', encoding='utf-8') as f:
        f.write(xml_header)

        for award in sucess_extracted_awards:
            f.write(f"{award}\n")
        f.write(xml_footer)
    


