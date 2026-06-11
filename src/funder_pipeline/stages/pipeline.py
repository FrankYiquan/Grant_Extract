from pathlib import Path
from funder_pipeline.stages.extract.fetch_openAlex import export_awards_per_funder
from funder_pipeline.stages.extract.remove_invalid import filter_invalid_assets
from funder_pipeline.stages.load.import_linking import link_asset_awards, link_asset_awards_from_dir
from funder_pipeline.stages.transform.extract_awards import extract_all_awards, extract_tag, output_import_awards_xml
from funder_pipeline.stages.transform.routing import route_all_awards_to_handlers, route_single_award_to_handler
import logging
from funder_pipeline.utils.current_funder import funders
from funder_pipeline.utils.logging import log_stage, log_summary

logger = logging.getLogger(__name__)


def get_award_data(startYear, endYear, openAlex_id, institutionsId="I6902469"):
    """The main function to run the entire pipeline for a given funder and year range."""

    logger.info("")
    logger.info("=" * 80)
    logger.info(
        "PIPELINE RUN: funder_id=%s (%s-%s)",
        openAlex_id,
        startYear,
        endYear
    )
    logger.info("=" * 80)

    # 1. fetch assets info and associated award data from OpenAlex
    # a copy of data is stored
    funder_name, output_dir, assets_awards = export_awards_per_funder(
        funder_id=openAlex_id,
        institution_id=institutionsId,
        start_year=startYear,
        end_year=endYear
    )

    log_stage(
        "[1/4] OpenAlex Award Collection",
        {
            "Funder": funder_name,
            "Total Awards": len(assets_awards),
            "Output File": output_dir,
        }
    )

    # 2. Call the Espero API to filter out the assets that is not associated with a faculty (sometimes, it contains assets from a students)
    valid_awards, invalid_dois, invalid_asset_output_dir = filter_invalid_assets(
        assets_awards,
        funder_name,
        startYear,
        endYear
    )

    log_stage(
        "[2/4] Asset Validation",
        {
            "Valid Awards": len(valid_awards),
            "Invalid Asset": len(invalid_dois),
            "Invalid Asset File": invalid_asset_output_dir,
        }
    )

    # 3. Route the awards to different handlers based on the funder id or award ID patterns
    routing_outcomes, routing_outcomes_output_dir = route_all_awards_to_handlers(
        valid_awards,
        openAlex_id,
        funder_name,
        startYear,
        endYear
    )

    log_stage(
        "[3/4] Award Routing",
        {
            "Awards Routed": len(routing_outcomes),
            "Routing File": routing_outcomes_output_dir,
        }
    )

    # 4. extracted award through funder API and recrod award asset linking info
    # this step is important for the later asset import and linking in Espero
    extraction_summary = extract_all_awards(
        routing_outcomes,
        startYear,
        endYear,
        funder_name
    )

    log_stage(
        "[4/4] Award Extraction",
        {
            "Success": extraction_summary["success_count"],
            "Failed": extraction_summary["failed_count"],
            "Error": extraction_summary["error_count"],
            "Success File": extraction_summary["success_file"],
            "Failed File": extraction_summary["failed_file"],
            "Error File": extraction_summary["error_file"],
            "Link File": extraction_summary["link_file"],
        }
    )

    # final log summary
    log_summary(
        {
            "Funder": funder_name,
            "Years": f"{startYear}-{endYear}",
            "Awards Collected": len(assets_awards),
            "Valid Awards": len(valid_awards),
            "Invalid Awards": len(invalid_dois),
            "Awards Routed": len(routing_outcomes),
            "Extract Success": extraction_summary["success_count"],
            "Extract Failed": extraction_summary["failed_count"],
            "Extract Error": extraction_summary["error_count"],
        }
    )

    logger.info("")
    logger.info("=" * 80)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 80)

def run_extract_awards(args):
    get_award_data(
        startYear=args.start_year,
        endYear=args.end_year,
        openAlex_id=args.funder_id,
        institutionsId=args.institutions_id
    )

def get_one_award_data(award_id, funder_id, skip_routing=False):
    """A function to run the pipeline for a single award. This is useful for testing, debugging, and backfilling purposes."""
    
    logger.info("")
    logger.info("=" * 80)
    logger.info(
        "JOB RUN: funder_id=%s, award_id=%s, skip_routing=%s",
        funder_id,
        award_id,
        skip_routing,
    )
    logger.info("=" * 80)

    funder_name = funders[funder_id]["name"]
    handler = funders[funder_id]["handler"]

    # 1. route the award to the appropriate handler
    if skip_routing:
        routing_stage = None
        extraction_stage = "[1/1] Award Extraction"

        final_handler = handler
        final_funder_name = funder_name
        final_funder_id = funder_id

    else:
        routing_stage = "[1/2] Award Routing"
        extraction_stage = "[2/2] Award Extraction"

        final_handler, final_funder_name, final_funder_id = (
            route_single_award_to_handler(funder_id, award_id)
        )

        log_stage(
            routing_stage,
            {
                "Initial Funder": funder_name,
                "Final Funder": final_funder_name,
                "Final Funder ID": final_funder_id,
                "Handler": final_handler,
            },
        )

    # 2. Extract award
    xml_result = final_handler(award_id, final_funder_name)
    success = (
        xml_result is not None
        and extract_tag(xml_result, "amount") not in (None, "", "None")
    )

    if success:
        output_dir = (
            Path("outputs")
            / "import_awards"
            / "single"
            / f"{funder_id}_{award_id}_skip_{skip_routing}_single_imported_awards.csv"
        )
        output_import_awards_xml([xml_result], output_dir)


    log_stage(
        extraction_stage,
        {
            "Success": "✅" if success else "❌",
            "Output_dir": output_dir if success else "N/A",
        },
    )

    logger.info("")
    logger.info("=" * 80)
    logger.info("JOB COMPLETE")
    logger.info("=" * 80)

def run_extract_one_award(args):
    get_one_award_data(
        award_id=args.award_id,
        funder_id=args.funder_id,
        skip_routing=args.skip_routing,
    )