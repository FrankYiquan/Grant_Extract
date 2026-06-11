from pathlib import Path
from funder_pipeline.utils.logging import log_stage
import logging, requests, csv
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from funder_pipeline.utils.sqs_config import PRODUCTION_EXLIBRIS_API, SANDBOX_EXLIBRIS_API

# def import_all_asset_grant_linking(linking_file, api_key):

#     with open(linking_file, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)

#         #for row in reader:
#             # call the lining methiod 

logger = logging.getLogger(__name__)


def import_asset_grant_linking(asset_id, award_id, production=False):
    """
    Link a single award to a single asset.
    One API request = one asset + one award.
    """

    url = (
        f"https://api-na.hosted.exlibrisgroup.com/"
        f"esploro/v1/assets/{asset_id}?op=patch&action=add"
    )

    api_key = (
        PRODUCTION_EXLIBRIS_API
        if production
        else SANDBOX_EXLIBRIS_API
    )

    headers = {
        "Accept": "application/json",
        "Authorization": f"apikey {api_key}",
    }

    payload = {
        "records": [
            {
                "fundingreferenceList": [
                    {
                        "awardnumber": award_id
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        return True

    except requests.exceptions.RequestException as e:
        return False


def batch_import(asset_award_list, production=False):
    """
    asset_award_list format:

    [
        (asset_id, award_id),
        (asset_id, award_id),
        ...
    ]
    """

    successful_awards = []
    failed_awards = []

    with ThreadPoolExecutor(max_workers=20) as executor:

        future_to_award = {
            executor.submit(
                import_asset_grant_linking,
                asset_id,
                award_id,
                production,
            ): (asset_id, award_id)
            for asset_id, award_id in asset_award_list
        }

        for future in as_completed(future_to_award):

            asset_id, award_id = future_to_award[future]

            try:
                result = future.result()

                if result:
                    successful_awards.append(
                        (asset_id, award_id)
                    )
                else:
                    failed_awards.append(
                        (asset_id, award_id)
                    )

            except Exception as e:
                failed_awards.append(
                    (asset_id, award_id)
                )

    return successful_awards, failed_awards


def write_error_csv(error_path, failed_awards):
    """
    failed_awards:
    [
        (asset_id, award_id),
        ...
    ]
    """

    with open(
        error_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "asset_id",
                "award_id",
            ]
        )

        for asset_id, award_id in failed_awards:
            writer.writerow(
                [
                    asset_id,
                    award_id,
                ]
            )


def link_asset_award_by_csv(
    asset_award_linking_dir,
    production=False,
):
    """
    Read CSV and create one API request
    per asset-award pair.
    """

    csv_path = (
        Path("outputs")
        / "award_asset_links"
        / f"{asset_award_linking_dir}.csv"
    )

    asset_awards = []

    with open(
        csv_path,
        newline="",
        encoding="utf-8",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            asset_id = (
                row["doi"]
                .split("https://doi.org/")[-1]
                .strip()
            )

            award_id = row["award"].strip()

            asset_awards.append(
                (
                    asset_id,
                    award_id,
                )
            )

    success, failure = batch_import(
        asset_awards,
        production,
    )

    error_path = (
        Path("outputs")
        / "award_asset_links"
        / "error"
        / f"{asset_award_linking_dir}_error.csv"
    )

    if failure:
        write_error_csv(
            error_path,
            failure,
        )

    return success, failure, error_path


def link_award_asset_by_arg(
    award_list,
    asset_id,
    production=False,
):
    """
    One asset,
    many awards.
    """

    asset_awards = [
        (
            asset_id,
            award_id,
        )
        for award_id in award_list
    ]

    return batch_import(
        asset_awards,
        production,
    )


def run_link_asset_awards_by_arg(args):
    """
    Link one asset
    to manually supplied awards.
    """

    logger.info("")
    logger.info("=" * 80)

    logger.info(
        "JOB RUN: asset_id=%s, award_count=%s, environment=%s",
        args.asset_id,
        len(args.award_ids),
        "production" if args.production else "sandbox"
    )

    logger.info("=" * 80)

    success, failure = link_award_asset_by_arg(
        award_list=args.award_ids,
        asset_id=args.asset_id,
        production=args.production,
    )

    log_stage(
        "[1/1] Award Asset Linking",
        {
            "Total Awards": len(success) + len(failure),
            "Success Count": len(success),
            "Failure Count": len(failure),
            "Failed Awards": [
                award_id
                for _, award_id in failure
            ],
        },
    )

    logger.info("")
    logger.info("=" * 80)
    logger.info("JOB COMPLETE")
    logger.info("=" * 80)


def run_link_asset_awards_from_dir(args):
    """
    Link awards/assets from CSV.
    """

    logger.info("")
    logger.info("=" * 80)

    logger.info(
        "JOB RUN: asset_award_linking_dir=%s, environment=%s",
        args.asset_award_linking_dir,
        "production" if args.production else "sandbox"
    )

    logger.info("=" * 80)

    success, failure, error_path = (
        link_asset_award_by_csv(
            asset_award_linking_dir=args.asset_award_linking_dir,
            production=args.production,
        )
    )

    log_stage(
        "[1/1] Award Asset Linking",
        {
            "Total Awards": len(success) + len(failure),
            "Success Count": len(success),
            "Failure Count": len(failure),
            "Error File": (
                str(error_path)
                if failure
                else "n/a"
            ),
        },
    )

    logger.info("")

    if failure:
        logger.warning(
            "Failed award links written to: %s",
            error_path,
        )

    logger.info("=" * 80)
    logger.info("JOB COMPLETE")
    logger.info("=" * 80)