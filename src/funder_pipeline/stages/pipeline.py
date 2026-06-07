from funder_pipeline.stages.extract.fetch_openAlex import export_awards_per_funder
from funder_pipeline.stages.extract.remove_invalid import filter_invalid_assets
from funder_pipeline.stages.transform.extract_awards import extract_all_awards
from funder_pipeline.stages.transform.routing import route_all_awards_to_handlers
import logging

logger = logging.getLogger(__name__)


def get_award_data(startYear, endYear, openAlex_id, institutionsId="I6902469"):

    # 1. fetch assets info and associated award data from OpenAlex
    # a copy of data is stored
    funder_name, output_dir, assets_awards = export_awards_per_funder(
        funder_id=openAlex_id,
        institution_id=institutionsId,
        start_year=startYear,
        end_year=endYear
    )

    logger.info(
        "Assets and Awards info for %s exported to %s",
        funder_name,
        output_dir
    )
    logger.info(
        "Total awards for %s: %d",
        funder_name,
        len(assets_awards)
    )

    # 2. Call the Espero API to filter out the assets that is not associated with a faculty (sometimes, it contains assets from a students)
    valid_awards, invalid_dois, invalid_asset_output_dir = filter_invalid_assets(
        assets_awards,
        funder_name,
        startYear,
        endYear
    )

    logger.info(
        "Valid awards for %s: %d",
        funder_name,
        len(valid_awards)
    )
    logger.info(
        "Invalid awards for %s: %d; their doi are in %s",
        funder_name,
        len(invalid_dois),
        invalid_asset_output_dir
    )

    # 3. Route the awards to different handlers based on the funder id or award ID patterns
    routing_outcomes, routing_outcomes_output_dir = route_all_awards_to_handlers(
        valid_awards,
        openAlex_id,
        funder_name,
        startYear,
        endYear
    )

    logger.info(
        "Routing outcomes for %s saved to %s",
        funder_name,
        routing_outcomes_output_dir
    )

    # 4. extracted award through funder API and recrod award asset linking info
    # this step is important for the later asset import and linking in Espero
    extraction_summary = extract_all_awards(
        routing_outcomes,
        startYear,
        endYear,
        funder_name
    )

    logger.info(
        "After extraction, success: %d, failed: %d, error: %d",
        extraction_summary["success_count"],
        extraction_summary["failed_count"],
        extraction_summary["error_count"]
    )

    logger.info(
        "Extracted (success) awards saved to %s",
        extraction_summary["success_file"]
    )

    logger.info(
        "Failed awards saved to %s",
        extraction_summary["failed_file"]
    )

    logger.info(
        "Error awards saved to %s",
        extraction_summary["error_file"]
    )

    logger.info(
        "Award-Asset linking info saved to %s",
        extraction_summary["link_file"]
    )