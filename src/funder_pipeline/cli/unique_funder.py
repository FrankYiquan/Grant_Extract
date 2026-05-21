

from funder_pipeline.sideJobs.brandeis_funder import run_unique_funder


def register_unique_funder_command(subparsers):
    unique_funder_parser = subparsers.add_parser(
        "unique_funder",
        description="Get the count of unique funders for each year and output to a CSV file."
    )
    unique_funder_parser.add_argument(
        "--start_year",
        type=int,
        required=True,
        help="The start year for counting unique funders."
    )
    unique_funder_parser.add_argument(
        "--end_year",
        type=int,
        required=True,
        help="The end year for counting unique funders."
    )
    unique_funder_parser.add_argument(
        "--institutions_id",
        type=str,
        default="I6902469",
        help="The OpenAlex ID of the institution to filter by (default: Brandeis University)."
    )

    unique_funder_parser.set_defaults(func=run_unique_funder)
    

    


