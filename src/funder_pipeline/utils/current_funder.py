from funder_pipeline.handlers.Agence_Nationale_De_La_Recherche import extract_ANDLR_award
from funder_pipeline.handlers.Australian_Research_Council import extract_ARC_award
from funder_pipeline.handlers.Bill_and_Melinda_Gates_Foundation import extract_Bill_and_Melinda_Gates_Foundation_award
from funder_pipeline.handlers.European_Commision import extract_eu_commision_award
from funder_pipeline.handlers.Fondo_Nacional_de_Desarrollo_Científico_y_Tecnológico import extract_fondo_nacional_de_desarrollo_cientifico_y_tecnologico_award
from funder_pipeline.handlers.Japan_Society import extract_jsps_award
from funder_pipeline.handlers.John_Templeton_Foundation import extract_templeton_award
from funder_pipeline.handlers.Ministerio_De_Innovation import extract_MDI_award
from funder_pipeline.handlers.NSFC import extract_nsfc_award
from funder_pipeline.handlers.Narodowe_Centrum_Nauki import extract_NCN_award
from funder_pipeline.handlers.Nederlandse_Organisatie_voor_Wetenschappelijk_Onderzoek import extract_NOVWO_award
from funder_pipeline.handlers.Norges_Forskningsråd import extract_Norges_Forskningsrad_award
from funder_pipeline.handlers.Science_and_Technology_Facilities_Council import extract_Science_and_Technology_Facilities_Council_award
from funder_pipeline.handlers.Swedish_Research_Council import extract_Swedish_Research_Council_award
from funder_pipeline.handlers.Swiss_National_Science_Foundation import get_Swiss_National_Science_Foundation_grant
from funder_pipeline.handlers.TAGGS import extract_TAGGS_award
from funder_pipeline.handlers.US_Spending import extract_US_Spending_award
from funder_pipeline.handlers.NIH import activity_codes, ic_codes, extract_NIH_award
from funder_pipeline.handlers.NSF import extract_NSF_award

funders = {
    "F4320306076": {
        "name": "National Science Foundation",
        "prefixes": ["NSF", "AST", "OISE"],
        "regex": [r"^AST[-/]?\d+"],
        "handler": extract_NSF_award,
    },

    "F4320306080": {
        "name": "Foundation for the National Institutes of Health",
        "handler": extract_NIH_award,

    },

    "F4320306084": {
        "name": "U.S. Department of Energy",
        "prefixes": ["DE-", "AC02", "DOE"],
        "regex": [r"^DE[A-Z0-9\-]+"],
        "handler": extract_US_Spending_award,
    },

    "F4320306101": {
        "name": "National Aeronautics and Space Administration",
        "handler": extract_US_Spending_award,
    },

    "F4320306137": {
        "name": "Bill and Melinda Gates Foundation",
        "prefixes": ["INV", "OPP"],
        "handler": extract_Bill_and_Melinda_Gates_Foundation_award,
    },

    "F4320306193": {
        "name": "John Templeton Foundation",
        "handler": extract_templeton_award
    },

    "F4320309123": {
        "name": "Division of Intramural Research, National Institute of Allergy and Infectious Diseases",
        "handler": extract_NIH_award,
    },

    "F4320315062": {
        "name": "Ministerio de Ciencia, Innovación y Universidades",
        "handler": extract_MDI_award
    },

    "F4320317220": {
        "name": "National Energy Research Scientific Computing Center",
        "handler": extract_US_Spending_award,
    },

    "F4320318855": {
        "name": "National Institute of Mental Health and Neurosciences",
        "handler": extract_NIH_award,
    },

    "F4320320300": {
        "name": "European Commission",
        "handler": extract_eu_commision_award
    },

    "F4320320883": {
        "name": "Agence Nationale de la Recherche",
        "prefixes": ["ANR"],
        "handler": extract_ANDLR_award
    },

    "F4320320912": {
        "name": "Ministry of Education, Culture, Sports, Science and Technology",
        "handler": extract_jsps_award
    },

    "F4320320924": {
        "name": "Schweizerischer Nationalfonds zur Förderung der Wissenschaftlichen Forschung",
        "prefixes": ["SNSF", "PCEFP2", "P2SKP3", "P400PB", "IZRJZ3"],
        "handler": get_Swiss_National_Science_Foundation_grant
    },

    "F4320321001": {
        "name": "National Natural Science Foundation of China",
        "handler": extract_nsfc_award
    },

    "F4320321800": {
        "name": "Nederlandse Organisatie voor Wetenschappelijk Onderzoek",
        "prefixes": ["VI.Veni"],
        "handler": extract_NOVWO_award
    },

    "F4320321837": {
        "name": "Ministerio de Economía y Competitividad",
        "handler": extract_MDI_award
    },

    "F4320322511": {
        "name": "Narodowe Centrum Nauki",
        "prefixes": ["UMO", "NCN", "PPN", "PPO", "OPUS"],
        "handler": extract_NCN_award
    },

    "F4320322581": {
        "name": "Vetenskapsrådet",
        "handler": extract_Swedish_Research_Council_award
    },

    "F4320322930": {
        "name": "Ministerio de Ciencia e Innovación",
        "prefixes": ["SEV", "PGC", "MDM", "ESP", "MCIN", "AEI"],
        "handler": extract_MDI_award
    },

    "F4320323299": {
        "name": "Norges Forskningsråd",
        "handler": extract_Norges_Forskningsrad_award,
    },

    "F4320328499": {
        "name": "Narodowa Agencja Wymiany Akademickiej",
        "handler": extract_NCN_award
    },

    "F4320331146": {
        "name": "Agencia Nacional de Investigación y Desarrollo",
        "prefixes": ["FONDECYT"],
        "handler": extract_fondo_nacional_de_desarrollo_cientifico_y_tecnologico_award
    },

    "F4320332161": {
        "name": "National Institutes of Health",
        "prefixes": activity_codes + ic_codes,
        "handler": extract_NIH_award,
    },

    "F4320332162": {
        "name": "Centers for Disease Control and Prevention",
        "handler": extract_NIH_award,
    },

    "F4320332167": {
        "name": "Directorate for Biological Sciences",
        "handler": extract_NSF_award,
    },

    "F4320332169": {
        "name": "Directorate for Computer and Information Science and Engineering",
        "handler": extract_NSF_award,
    },

    "F4320332172": {
        "name": "Directorate for Mathematical and Physical Sciences",
        "handler": extract_NSF_award,
    },

    "F4320332173": {
        "name": "Directorate for Social, Behavioral and Economic Sciences",
        "handler": extract_NSF_award,
    },

    "F4320332178": {
        "name": "National Institute of Standards and Technology",
        "handler": extract_NIH_award,
    },

    "F4320332180": {
        "name": "Defense Advanced Research Projects Agency",
        "handler": extract_US_Spending_award,
    },

    "F4320332359": {
        "name": "Office of Science",
        "handler": extract_US_Spending_award,
    },

    "F4320332369": {
        "name": "National Nuclear Security Administration",
        "handler": extract_US_Spending_award,
    },

    "F4320332999": {
        "name": "Horizon 2020 Framework Programme",
        "handler": extract_eu_commision_award,
    },

    "F4320333065": {
        "name": "Seventh Framework Programme",
        "handler": extract_eu_commision_award,
    },

    "F4320334627": {
        "name": "Engineering and Physical Sciences Research Council",
        "handler": extract_Science_and_Technology_Facilities_Council_award
    },

    "F4320334629": {
        "name": "Biotechnology and Biological Sciences Research Council",
        "handler": extract_Science_and_Technology_Facilities_Council_award
    },

    "F4320334632": {
        "name": "Science and Technology Facilities Council",
        "prefixes": ["ST/", "PP/"],
        "keywords": ["ATLAS", "ATLAS Upgrades", "GRIDPP"],
        "handler": extract_Science_and_Technology_Facilities_Council_award
    },

    "F4320334678": {
        "name": "European Research Council",
        "prefixes": ["ERC", "FP7"],
        "handler": extract_eu_commision_award,
    },

    "F4320334704": {
        "name": "Australian Research Council",
        "prefixes": ["DP", "CE"],
        "handler": extract_ARC_award,
    },

    "F4320334764": {
        "name": "Japan Society for the Promotion of Science",
        "handler": extract_jsps_award,
    },

    "F4320335254": {
        "name": "Horizon 2020",
        "handler": extract_eu_commision_award,
    },

    "F4320335322": {
        "name": "European Regional Development Fund",
        "handler": extract_eu_commision_award,
    },

    "F4320337330": {
        "name": "National Institute on Alcohol Abuse and Alcoholism",
        "handler": extract_NIH_award,
    },

    "F4320337337": {
        "name": "National Institute on Aging",
        "handler": extract_NIH_award,
    },

    "F4320337338": {
        "name": "National Heart, Lung, and Blood Institute",
        "handler": extract_NIH_award,
    },

    "F4320337345": {
        "name": "Office of Naval Research",
        "handler": extract_US_Spending_award,
    },

    "F4320337346": {
        "name": "National Institute of Mental Health",
        "handler": extract_NIH_award,
    },

    "F4320337347": {
        "name": "National Institute on Drug Abuse",
        "handler": extract_NIH_award,
    },

    "F4320337350": {
        "name": "National Eye Institute",
        "handler": extract_NIH_award,
    },

    "F4320337351": {
        "name": "National Cancer Institute",
        "handler": extract_NIH_award,
    },

    "F4320337352": {
        "name": "National Institute on Deafness and Other Communication Disorders",
        "handler": extract_NIH_award,
    },

    "F4320337354": {
        "name": "National Institute of General Medical Sciences",
        "handler": extract_NIH_award,
    },

    "F4320337355": {
        "name": "National Institute of Allergy and Infectious Diseases",
        "handler": extract_NIH_award,
    },

    "F4320337357": {
        "name": "National Institute of Diabetes and Digestive and Kidney Diseases",
        "handler": extract_NIH_award,
    },

    "F4320337359": {
        "name": "National Institute of Neurological Disorders and Stroke",
        "handler": extract_NIH_award,
    },

    "F4320337361": {
        "name": "National Institute of Environmental Health Sciences",
        "handler": extract_NIH_award,
    },

    "F4320337362": {
        "name": "National Institute of Arthritis and Musculoskeletal and Skin Diseases",
        "handler": extract_NIH_award,
    },

    "F4320337363": {
        "name": "National Institute of Biomedical Imaging and Bioengineering",
        "handler": extract_NIH_award,
    },

    "F4320337364": {
        "name": "National Institute of Child Health and Human Development",
        "handler": extract_TAGGS_award,
    },

    "F4320337366": {
        "name": "Division of Social and Economic Sciences",
        "handler": extract_NSF_award,
    },

    "F4320337367": {
        "name": "Division of Materials Research",
        "handler": extract_NSF_award,
    },

    "F4320337368": {
        "name": "Division of Graduate Education",
        "handler": extract_NSF_award,
    },

    "F4320337370": {
        "name": "Office of International Science and Engineering",
        "handler": extract_NSF_award,
    },

    "F4320337372": {
        "name": "U.S. National Library of Medicine",
        "handler": extract_NIH_award,
    },

    "F4320337377": {
        "name": "Office of Advanced Cyberinfrastructure",
        "handler": extract_NSF_award,
    },

    "F4320337380": {
        "name": "Division of Mathematical Sciences",
        "handler": extract_NSF_award
    },

    "F4320337386": {
        "name": "Division of Ocean Sciences",
        "handler": extract_NSF_award,
    },

    "F4320337387": {
        "name": "Division of Computing and Communication Foundations",
        "handler": extract_NSF_award,
    },

    "F4320337390": {
        "name": "Division of Chemical, Bioengineering, Environmental, and Transport Systems",
        "handler": extract_NSF_award,
    },

    "F4320337393": {
        "name": "Division of Chemistry",
        "handler": extract_NSF_award,
    },

    "F4320337396": {
        "name": "Division of Industrial Innovation and Partnerships",
        "handler": extract_NSF_award,
    },

    "F4320337397": {
        "name": "Division of Molecular and Cellular Biosciences",
        "handler": extract_NSF_award,
    },

    "F4320337398": {
        "name": "Division of Biological Infrastructure",
        "handler": extract_NSF_award,
    },

    "F4320337408": {
        "name": "Division of Undergraduate Education",
        "handler": extract_NSF_award,
    },

    "F4320337480": {
        "name": "Basic Energy Sciences",
        "handler": extract_US_Spending_award,
    },

    "F4320337511": {
        "name": "High Energy Physics",
        "handler": extract_US_Spending_award,
    },

    "F4320337544": {
        "name": "Office of Extramural Research, National Institutes of Health",
        "handler": extract_NIH_award,
    },

    "F4320337593": {
        "name": "National Center for Complementary and Integrative Health",
        "handler": extract_NIH_award,
    },

    "F4320337604": {
        "name": "National Institute on Disability, Independent Living, and Rehabilitation Research",
        "handler": extract_TAGGS_award,
    },

    "F4320337611": {
        "name": "Eunice Kennedy Shriver National Institute of Child Health and Human Development",
        "handler": extract_NIH_award,
    },

    "F4320338073": {
        "name": "Fondo Nacional de Desarrollo Científico y Tecnológico",
        "handler": extract_fondo_nacional_de_desarrollo_cientifico_y_tecnologico_award
    },

    "F4320338279": {
        "name": "Air Force Office of Scientific Research",
        "handler": extract_US_Spending_award,
    },

    "F4320338281": {
        "name": "Army Research Office",
        "handler": extract_US_Spending_award,
    },

    "F4320338284": {
        "name": "Argonne National Laboratory",
        "handler": extract_US_Spending_award,
    },

    "F4320338292": {
        "name": "Lawrence Berkeley National Laboratory",
        "handler": extract_US_Spending_award,
    },

    "F4320338304": {
        "name": "Los Alamos National Laboratory",
        "handler": extract_US_Spending_award,
    },

    "F4320338335": {
        "name": "H2020 European Research Council",
        "handler": extract_eu_commision_award,
    },

    "F4320338337": {
        "name": "H2020 Marie Skłodowska-Curie Actions",
        "handler": extract_eu_commision_award,
    },

    "F4320338381": {
        "name": "SLAC National Accelerator Laboratory",
        "handler": extract_US_Spending_award,
    },

    "F4320338412": {
        "name": "Division of Microbiology and Infectious Diseases, National Institute of Allergy and Infectious Diseases",
        "handler": extract_NIH_award,
    },

    "F4320338438": {
        "name": "HORIZON EUROPE Marie Sklodowska-Curie Actions",
        "handler": extract_eu_commision_award,
    },

    "F4320338453": {
        "name": "HORIZON EUROPE European Research Council",
        "handler": extract_eu_commision_award,
    },

    "F4320306085": {
        "name": "U.S. Department of Health and Human Services",
        "prefixes": ["NU", "U48"],
        "regex": [r"^90[A-Za-z]{2}"],
        "handler": extract_TAGGS_award
    },

    "F4320306078": {
        "name": "U.S. Department of Defense",
        "handler": extract_US_Spending_award,
    },
}