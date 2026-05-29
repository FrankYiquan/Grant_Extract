from funder_pipeline.cli.common import add_common_grant_args, parse_funder_id, validate_year_range
from funder_pipeline.sideJobs.brandeis_funder import run_unique_funder, run_award_per_funder

def register_unique_funder_command(subparsers):
    parser = subparsers.add_parser(
        "unique_funder",
        description=(
            "Get counts of unique funders "
            "and export results to CSV."
        )
    )

    add_common_grant_args(parser)

    parser.set_defaults(
        func=run_unique_funder,
        validate_func=validate_year_range,
        parser=parser
    )


def register_funder_awards_command(subparsers):
    parser = subparsers.add_parser(
        "award_per_funder",
        description=(
            "Get award numbers for a specific funder."
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
        func=run_award_per_funder,
        validate_func=validate_year_range,
        parser=parser
    )