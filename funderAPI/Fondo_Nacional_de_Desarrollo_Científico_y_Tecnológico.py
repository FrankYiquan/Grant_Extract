import pandas as pd
import re


def get_fondo_nacional_de_desarrollo_cientifico_y_tecnologico_grant(grantId):
    df = pd.read_csv("resources/BDH_HISTORICA.csv", sep=";")
    records = df.to_dict(orient="records")

    #normalize grantId
    normalized_grantId = re.search(r"\d.*", grantId).group(0).strip()


    for record in records:
        if record["CODIGO_PROYECTO"] == normalized_grantId:
            return {
                "title": record["NOMBRE_PROYECTO"],
                "amount": record["MONTO_ADJUDICADO"],
                "startDate": record["AGNO_CONCURSO"],
                "currency": "CLP"
            }
    
    return "cannot be found"



# print(get_fondo_nacional_de_desarrollo_cientifico_y_tecnologico_grant("FONDECYT 1210400"))

