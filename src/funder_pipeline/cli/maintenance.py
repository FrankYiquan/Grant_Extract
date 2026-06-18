from funder_pipeline.stages.maintenance.clean_outputs import run_clean_outputs


def register_clean_outputs_command(subparsers):
    parser = subparsers.add_parser(
        "clean_outputs",
        description=(
            "Delete files inside outputs/ and its subfolders while preserving "
            "the directory structure."
        ),
    )

    parser.add_argument(
        "--dry_run",
        action="store_true",
        default=False,
        help="List files that would be deleted without removing them.",
    )

    parser.set_defaults(
        func=run_clean_outputs,
        parser=parser,
    )
