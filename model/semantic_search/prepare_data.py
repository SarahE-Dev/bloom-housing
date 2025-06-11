import json
import logging
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

providers = [
    {
        "Provider": "City of LA Community Investments for Families Department (LA, CIFD) (1200 W. 7th St., 4th Floor)",
        "Services": "Food/Nutrition Services Food Stamps Child/Youth Services Tutoring Employment Services Resume preparation Child/Youth Services Mentoring Emergency Services Violence protection assistance Health Services Dental Care Employment Services Job seeking resources Education Services High school certificate or diploma Housing Services Domestic violence shelters Income Management Services Earned Income Tax Credit Income Management Services Banking Emergency Services Temporary shelter Emergency Services Food Income Management Services Financial management Education Services English Language Proficiency Food/Nutrition Services Food Banks Other Services Citizenship Child/Youth Services Before/ After school programs Emergency Services Legal assistance Employment Services Job placement Employment Services Job skills training",
    },
    {
        "Provider": "County of Los Angeles Department of Public Social Services (12860 Crossroads Pkwy. South)",
        "Services": "Health Services Substance abuse education and counseling Senior Services Meal Delivery Child/Youth Services Youth employment Emergency Services Utility assistance Senior Services In-home assistance Employment Services Interview preparation Employment Services Resume preparation Food/Nutrition Services Meal Delivery Child/Youth Services Tutoring Emergency Services Violence protection assistance Health Services Domestic violence counseling Emergency Services Rental assistance Child/Youth Services Mentoring Employment Services Job seeking resources Emergency Services Clothing distribution Senior Services Congregate Meals Housing Services Domestic violence shelters Housing Services Transitional housing Emergency Services Temporary shelter Emergency Services Food Homeless Services Shelters Emergency Services Mortgage assistance Health Services Mental Health Care Housing Services Eviction assistance Child/Youth Services Before/ After school programs Emergency Services Legal assistance Employment Services Job placement Employment Services Job skills training",
    },
    {
        "Provider": "Foothill Unity Center, Inc (790 West Chestnut Ave.)",
        "Services": "Emergency Services Transportation assistance Food/Nutrition Services Nutrition education Emergency Services Utility assistance Food/Nutrition Services Food Stamps Child/Youth Services School Supplies Food/Nutrition Services Meal Delivery Homeless Services Housing Services Child/Youth Services Mentoring Emergency Services Violence protection assistance Emergency Services Rental assistance Health Services Dental Care Emergency Services Clothing distribution Child/Youth Services Services for Emancipated youth Health Services Screenings Income Management Services Earned Income Tax Credit Health Services Vaccinations Homeless Services Motel vouchers Emergency Services Temporary shelter Emergency Services Food Food/Nutrition Services Food Banks Emergency Services Medical assistance Emergency Services Mortgage assistance Homeless Services Transportation Emergency Services Legal assistance Employment Services Job skills training Income Management Services Tax Preparation",
    },
    {
        "Provider": "Long Beach Community Action Partnership (117 West Victoria Street)",
        "Services": "Child/Youth Services Youth employment Child/Youth Services Mentoring Child/Youth Services Before/ After school programs Emergency Services Utility assistance Food/Nutrition Services Food Stamps Income Management Services Earned Income Tax Credit Income Management Services Self Sufficiency Calculator Income Management Services Tax Preparation Energy Services Assistance with residential utility bill payment Energy Services Home Weatherization Energy Services Emergency assistance with residential energy-related crisis (utility shut-off notices, energy-related life-threatening emergency) Water Services Assistance with residential water and wastewater utility bill payment. Availability of LIHWAP services is subject to water or wastewater system participation, household eligibility, availability of funding, and other factors.",
    },
    {
        "Provider": "Maravilla Foundation (5729 E. Union Pacific Ave.)",
        "Services": "Energy Services Assistance with residential utility bill payment Energy Services Home Weatherization Energy Services Emergency assistance with residential energy-related crisis (utility shut-off notices, energy-related life-threatening emergency) Water Services Assistance with residential water and wastewater utility bill payment. Availability of LIHWAP services is subject to water or wastewater system participation, household eligibility, availability of funding, and other factors.",
    },
    {
        "Provider": "Pacific Asian Consortium in Employment (PACE) (1055 Wilshire Blvd., Ste. 900E)",
        "Services": "Energy Services Assistance with residential utility bill payment Energy Services Home Weatherization Energy Services Emergency assistance with residential energy-related crisis (utility shut-off notices, energy-related life-threatening emergency) Water Services Assistance with residential water and wastewater utility bill payment. Availability of LIHWAP services is subject to water or wastewater system participation, household eligibility, availability of funding, and other factors.",
    },
    {
        "Provider": "Workforce Development, Aging and Community Services (LANAIC) (3175 W. 6th St., Room 403) ",
        "Services": "Senior Services Transportation Emergency Services Food Emergency Services Transportation assistance Child/Youth Services School Supplies Transportation Services Gas vouchers Emergency Services Disaster relief Emergency Services Medical assistance Senior Services Congregate Meals Senior Services Holiday food baskets Health Services Domestic violence counseling Emergency Services Rental assistance Other Services Anti-Gang programs Child/Youth Services Before/ After school programs Emergency Services Utility assistance Senior Services In-home assistance Transportation Services Bus passes Homeless Services Motel vouchers Emergency Services Temporary shelter",
    },
]

# Base directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_and_save_data():
    model_name = "all-MiniLM-L6-v2"
    output_providers_path = os.path.join(BASE_DIR, "providers.json")
    output_embeddings_path = os.path.join(BASE_DIR, "embeddings.npy")

    try:
        logger.info(f"Loading sentence transformer model: {model_name}")
        model = SentenceTransformer(model_name)

        logger.info("Creating service embeddings...")
        texts = [f"{entry['Provider']}. {entry['Services']}" for entry in providers]
        embeddings = model.encode(texts, show_progress_bar=True)

        logger.info(f"Successfully created embeddings with shape: {embeddings.shape}")

        logger.info(f"Saving providers data to {output_providers_path}...")
        with open(output_providers_path, "w") as f:
            json.dump(providers, f, indent=4)
        logger.info("Providers data saved.")

        logger.info(f"Saving embeddings to {output_embeddings_path}...")
        np.save(output_embeddings_path, embeddings)
        logger.info("Embeddings saved.")

    except Exception as e:
        logger.critical(f"Failed during data preparation: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting data preparation process...")
    generate_and_save_data()
    logger.info("Data preparation process completed.")
