import argparse

DEFAULT_INSTITUTION_ID = "I6902469"

def parse_year(value):
    if value == "all":
        return value
    
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Year must be an integer or 'all'"
        )

def validate_year_range(args, parser):
    if (isinstance(args.start_year, int) and isinstance(args.end_year, int) and args.start_year > args.end_year):
        parser.error(
            "--start_year must be less than or equal to --end_year"
        )

def add_common_grant_args(parser):
    parser.add_argument(
        "--start_year",
        type=parse_year,
        required=True,
        help="The start year."
    )

    parser.add_argument(
        "--end_year",
        type=parse_year,
        required=True,
        help="The end year."
    )

    parser.add_argument(
        "--institutions_id",
        type=str,
        default=DEFAULT_INSTITUTION_ID,
        help="OpenAlex institution ID."
    )