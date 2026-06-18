# Funder API Pipeline

## Purpose

This tool streamlines the scholarly librarian effort and time required to import awards or grants associated with academic articles, called assets in Esploro. It is a data pipeline that starts from scholarly article metadata, identifies funder award IDs, extracts structured award information, and prepares the files needed to import awards and link them back to assets in Esploro.

The pipeline currently supports 97 funders. For each supported funder, award information is extracted either through a direct funder API call or, when an API is not available, through web scraping. The supported funder API tracking sheet is here:

https://docs.google.com/spreadsheets/d/10ehJgOiP2DjTQb045rAi50PwteY5Zq8tbDYAxT37Ik4/edit?gid=0#gid=0

The default institution is Brandeis University, using OpenAlex institution ID `I6902469`.

## CLI Commands

The project installs a console command named `fp`.

| Command | Meaning | Example |
| --- | --- | --- |
| `fp unique_funder` | Find unique funders for an institution and year range, then write a funder count CSV. | `fp unique_funder --start_year 2018 --end_year 2024` |
| `fp award_per_funder` | Fetch OpenAlex assets and award IDs for one supported funder in a year range. | `fp award_per_funder --funder_id F4320306076 --start_year 2018 --end_year 2024` |
| `fp extract_awards` | Run the main extraction pipeline for one funder: collect awards, validate Esploro assets, route awards to handlers, extract award metadata, and write import/linking outputs. | `fp extract_awards --funder_id F4320306076 --start_year 2018 --end_year 2024` |
| `fp extract_one_award` | Extract metadata for a single award. Useful for testing, debugging, and backfills. | `fp extract_one_award --funder_id F4320306076 --award_id 1144085` |
| `fp extract_one_award --skip_routing` | Extract one award with the handler for the provided funder ID, bypassing routing rules. | `fp extract_one_award --funder_id F4320306076 --award_id 1144085 --skip_routing` |
| `fp get_asset_id` | Look up an Esploro asset ID by DOI. Accepts either a plain DOI or a `https://doi.org/` URL. | `fp get_asset_id --doi 10.1038/s41467-020-17432-w` |
| `fp link_assets_by_arg` | Link one Esploro asset to one or more award IDs through the Ex Libris API. Uses sandbox unless `--production` is supplied. | `fp link_assets_by_arg --asset_id 9924303240601921 --award_ids 1144085 AST-1337663` |
| `fp link_asset_awards_from_csv` | Link asset-award pairs from `outputs/award_asset_links/<name>.csv`. Uses sandbox unless `--production` is supplied. | `fp link_asset_awards_from_csv --dir "National Science Foundation_2018_2024_award_asset_links"` |
| `fp clean_outputs` | Delete files inside `outputs/` and all subfolders while preserving the folder structure. | `fp clean_outputs` |
| `fp clean_outputs --dry_run` | Preview which files would be deleted without removing anything. | `fp clean_outputs --dry_run` |

Common arguments:

- `--start_year` and `--end_year` are required for funder discovery and extraction commands.
- `--institutions_id` is optional and defaults to `I6902469`.
- `--funder_id` must be one of the supported OpenAlex funder IDs configured in `src/funder_pipeline/utils/current_funder.py`.
- Add `--production` only when you intend to write to the production Ex Libris/Esploro environment.

## Setup

Create the Conda environment:

```bash
conda env create -f environment.yml
```

Activate the environment:

```bash
conda activate Funder_API
```

Install the package locally so the `fp` command is available:

```bash
pip install -e .
```

Deactivate the environment when finished:

```bash
conda deactivate
```

## Running the Pipeline

1. Find funders and award counts for a year range:

```bash
fp unique_funder --start_year 2018 --end_year 2024
```

This writes:

```text
outputs/funder_count/unique_funders_2018_2024.csv
```

2. Inspect awards for a specific funder:

```bash
fp award_per_funder --funder_id F4320306076 --start_year 2018 --end_year 2024
```

This writes:

```text
outputs/award_ids/<funder_name>_2018_2024_funded_awards.csv
```

3. Run the full extraction pipeline for a funder:

```bash
fp extract_awards --funder_id F4320306076 --start_year 2018 --end_year 2024
```

The full pipeline performs four stages:

1. Collect assets and award IDs from OpenAlex.
2. Validate that each DOI maps to an Esploro asset.
3. Route each award to the correct funder handler.
4. Extract award metadata and write Esploro import/linking outputs.

4. Import successful awards into Esploro using the generated XML-formatted file in:

```text
outputs/import_awards/success/
```

5. Link imported awards back to assets:

```bash
fp link_asset_awards_from_csv --dir "<funder_name>_2018_2024_award_asset_links"
```

Use production only when ready:

```bash
fp link_asset_awards_from_csv --dir "<funder_name>_2018_2024_award_asset_links" --production
```

## Output Files

Main runtime outputs are written under `outputs/`:

| Path | Contents |
| --- | --- |
| `outputs/funder_count/` | Unique funder counts for an institution and year range. |
| `outputs/award_ids/` | OpenAlex assets and raw funder award IDs for a selected funder. |
| `outputs/invalid_assets/` | DOI values that could not be validated as Esploro assets. |
| `outputs/routing_outcomes/` | Routing decisions showing the initial funder, final funder, handler, and whether routing changed. |
| `outputs/import_awards/success/` | Successfully extracted awards formatted for Esploro import. |
| `outputs/import_awards/failure/` | Awards that were processed but did not return enough metadata to import. |
| `outputs/import_awards/error/` | Awards that raised errors during extraction. |
| `outputs/import_awards/single/` | Output from `extract_one_award`. |
| `outputs/award_asset_links/` | Award-to-asset links used after awards are imported. |
| `outputs/award_asset_links/error/` | Failed award-to-asset link attempts. |

To clear generated output files without deleting the folders, run:

```bash
fp clean_outputs
```

To preview the cleanup first, run:

```bash
fp clean_outputs --dry_run
```

## Project Structure

```text
.
|-- environment.yml
|-- pyproject.toml
|-- docker-compose.yaml
|-- airflow/
|   |-- dags/
|   |-- Dockerfile
|   `-- requirements.txt
|-- outputs/
|   |-- award_asset_links/
|   |-- award_ids/
|   |-- funder_count/
|   |-- import_awards/
|   |-- invalid_assets/
|   `-- routing_outcomes/
`-- src/funder_pipeline/
    |-- main.py
    |-- cli/
    |-- handlers/
    |-- resources/
    |-- stages/
    |   |-- extract/
    |   |-- transform/
    |   `-- load/
    `-- utils/
```

Important modules:

- `src/funder_pipeline/main.py` registers the `fp` CLI and subcommands.
- `src/funder_pipeline/cli/` defines CLI arguments and command registration.
- `src/funder_pipeline/stages/extract/` collects OpenAlex data and validates assets in Esploro.
- `src/funder_pipeline/stages/transform/` routes awards and extracts structured award metadata.
- `src/funder_pipeline/stages/load/` links awards back to Esploro assets through the Ex Libris API.
- `src/funder_pipeline/handlers/` contains funder-specific extraction logic.
- `src/funder_pipeline/utils/current_funder.py` maps supported OpenAlex funder IDs to funder names, routing rules, and handlers.
- `src/funder_pipeline/resources/` contains supporting lookup data, including funder code mappings.
- `airflow/dags/` contains Airflow DAGs for orchestrated ETL runs.

## External Services

The pipeline depends on several external systems:

- OpenAlex API for scholarly article, DOI, funder, and award metadata.
- Funder APIs or web pages for detailed award metadata.
- Ex Libris Esploro API for asset validation and award-to-asset linking.
- AWS SQS for queue-based processing paths used by some pipeline code.

API keys and queue URLs are configured in `src/funder_pipeline/utils/sqs_config.py`. Review this file before running against sandbox or production environments, and manage credentials securely for shared deployments.
