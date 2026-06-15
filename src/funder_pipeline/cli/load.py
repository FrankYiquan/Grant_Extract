from funder_pipeline.cli.common import validate_doi_format
from funder_pipeline.stages.extract.remove_invalid import run_get_assetID_by_doi
from funder_pipeline.stages.load.import_linking import run_link_asset_awards_by_arg, run_link_asset_awards_from_dir
from pathlib import Path
import argparse

def register_link_asset_awards_command(subparsers):
    parser = subparsers.add_parser(
        "link_assets_by_arg",
        description=(
            "Link one asset to one or more manually provided award IDs."
        )
    )

    parser.add_argument(
        "--asset_id",
        type=str,
        required=True,
        help="The Esploro asset ID to update."
    )

    parser.add_argument(
        "--award_ids",
        nargs="+",
        required=True,
        help="One or more award IDs to link to the asset."
    )

    parser.add_argument(
        "--production",
        action="store_true",
        default=False,
        help="Use the production Ex Libris API key instead of sandbox."
    )

    parser.set_defaults(
        func=run_link_asset_awards_by_arg,
        parser=parser
    )

def existing_award_asset_csv(value):
    csv_path = (
        Path("outputs")
        / "award_asset_links"
        / f"{value}.csv"
    )

    if not csv_path.exists():
        raise argparse.ArgumentTypeError(
            f"CSV file does not exist: {csv_path}"
        )

    return value

def register_link_asset_awards_from_dir_command(subparsers):
    parser = subparsers.add_parser(
        "link_asset_awards_from_csv",
        description=(
            "Link award/assets from outputs/award_asset_links/<name>.csv."
        )
    )

    parser.add_argument(
        "--dir",
        type=existing_award_asset_csv,
        required=True,
        help="CSV filename stem under outputs/award_asset_links, without .csv."
    )

    parser.add_argument(
        "--production",
        action="store_true",
        default=False,
        help="Use the production Ex Libris API key instead of sandbox."
    )

    parser.set_defaults(
        func=run_link_asset_awards_from_dir,
        parser=parser
    )

def register_get_assetID_by_doi(subparsers):
    parser = subparsers.add_parser(
        "get_asset_id",
        description=(
            "Get Asset ID of Espero through asset's doi"
        )
    )

    parser.add_argument(
        "--doi",
        type=validate_doi_format,
        help="Input either the pure doi or doi starts with https://doi.org/"
    )

    parser.set_defaults(
        func=run_get_assetID_by_doi,
        parser=parser
    )
