FUNDER_PATTERNS = {
    "Ministerio de Ciencia e Innovación":{
        "prefixes": ["SEV", "PGC", "MDM"],
    },

    "Science_and_Technology_Facilities_Council": {
        "prefixes": ["ST/", "PP/"],
        "keywords": ["ATLAS", "ATLAS Upgrades", "GRIDPP"],
    },

    "European_Research_Council": {
        "prefixes": ["ERC", "FP7"],
    },

    "Department_of_Energy": {
        "prefixes": ["DE-", "AC02", "DOE"],
        "regex": [r"^DE[A-Z0-9\-]+"],
    },

    "Ministerio_de_Ciencia_e_Innovación": {
        "prefixes": ["MCIN"],
    },

    "Swiss_National_Science_Foundation": {
        "prefixes": ["SNSF", "PCEFP2", "P2SKP3", "P400PB", "IZRJZ3"],
    },

    "National_Science_Foundation": {
        "prefixes": ["NSF", "AST"],
        "regex": [
            r"^AST[-/]?\d+"
        ],
    },

    "TAGGS": {
        "prefixes": ["NU", "U48"],
        "regex": [
            r"^90[A-Za-z]{2}"
        ],
    },

    "National_Institutes_of_Health": {
        "regex": [
            r"^[A-Z]\d{2}[A-Z]{2}\d{6}$"
        ],
    },

    "Nederlandse_Organisatie_voor_Wetenschappelijk_Onderzoek": {
        "prefixes": ["VI.Veni"],
    },

    "Bill_and_Melinda_Gates_Foundation": {
        "prefixes": ["INV"],
    },

    "Agence_Nationale_de_la_Recherche": {
        "prefixes": ["ANR"],
    },

    "Australian_Research_Council": {
        "prefixes": ["DP", "CE"],
    },

    "Bill_and_Melinda_Gates_Foundation": {
        "prefixes": ["INV", "OPP"],
    }
}