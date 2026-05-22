import pandas as pd
import re
from funder_pipeline.utils.helper import escape_xml, add_months
from funder_pipeline.funderAPI.helper.schema_extract import (
    get_grant_status_from_end_date,
    get_matched_funder_code,
)
from pathlib import Path


award_csv = (
    Path("src")
    / "funder_pipeline"
    / "resources"
    / "BDH_HISTORICA.csv"
)

def get_fondo_nacional_de_desarrollo_cientifico_y_tecnologico_grant(award_id, funder_name):
    df = pd.read_csv(award_csv, sep=";")
    records = df.to_dict(orient="records")

    #normalize grantId
    normalized_award_id_search = re.search(r"\d.*", award_id)
    normalized_award_id = normalized_award_id_search.group(0) if normalized_award_id_search else award_id

    amount = None
    startDate = None
    endDate = None
    principal_investigator = None
    grant_url = None
    title = None
    funderCode = get_matched_funder_code(funder_name)
    status = "ACTIVE"

    for record in records:
        if record["CODIGO_PROYECTO"] == normalized_award_id:
            title = escape_xml(record["NOMBRE_PROYECTO"])
            amount = record["MONTO_ADJUDICADO"]
            startDate = f"{record['AGNO_CONCURSO']}-01-01"
            endDate = add_months(startDate, record["DURACION_MESES"])
            status = get_grant_status_from_end_date(endDate)
            # principal_investigator = record["INOMBRE_RESPONSABLE"]

    result = f"""<grant>
    <grantId>{normalized_award_id}</grantId>
    <grantName>{title}</grantName>
    <funderCode>{funderCode}</funderCode>
    <currencyOfAmount>researchgrant.currency.clp</currencyOfAmount>
    <amount>{amount}</amount>
    <startDate>{startDate}</startDate>
    <endDate>{endDate}</endDate>
    <grantURL>{grant_url}</grantURL>
    <profileVisibility>true</profileVisibility>
    <status>{status}</status>
</grant>"""
        
    return result


print(get_fondo_nacional_de_desarrollo_cientifico_y_tecnologico_grant("FONDECYT 1820247", "Agencia Nacional de Investigación y Desarrollo"))

