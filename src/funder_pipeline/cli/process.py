from funder_pipeline.cli.common import add_common_grant_args, parse_funder_id, validate_year_range
from funder_pipeline.stages.pipeline import run_extract_awards

def register_extract_awards_command(subparsers):
    parser = subparsers.add_parser(
        "extract_awards",
        description=(
            "Extract award information for a specific funder and year range."
        )
    )

    add_common_grant_args(parser)

    parser.add_argument(
        "--funder_id",
        type=parse_funder_id,
        required=True,
        help="The OpenAlex ID of the funder."
    )

    parser.set_defaults(
        func=run_extract_awards,
        validate_func=validate_year_range,
        parser=parser
    )