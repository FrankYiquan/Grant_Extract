from airflow import DAG
from airflow.decorators import task
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from datetime import datetime

from main import send_grant_sqs_for_one_funder
from sideJobs.brandeis_funder import get_all_funders   # YOU MUST PROVIDE THIS


with DAG(
    dag_id="funder_award_queue_dispatcher",
    start_date=datetime(2025, 11, 9),
    schedule_interval=None,
    catchup=False,
    tags=["funder", "sqs", "pipeline", "databricks"],
    params={
        "funderId": None,        # None or "all" or specific id
        "funderName": None,      # None or "all" or specific name
        "institutionsId": "I6902469",
        "startYear": 2017,
        "endYear": 2025,
    }
):

    # -------------------------------------------------
    # Step 1 — Determine funder list
    # -------------------------------------------------
    @task
    def prepare_funder_list(funderId, funderName):
        if funderId == "all" or funderName == "all":
            # Return ALL funders for dynamic mapping
            return get_all_funders()   # ← must return [{id, name}, ...]
        else:
            # Return list with one funder
            return [{"id": funderId, "name": funderName}]


    # -------------------------------------------------
    # Step 2 — Expand task to process each funder in parallel
    # -------------------------------------------------
    @task
    def dispatch_one_funder(funder, institutionsId, startYear, endYear):
        return send_grant_sqs_for_one_funder(
            funderId=funder["id"],
            funderName=funder["name"],
            institutionsId=institutionsId,
            startyear=startYear,
            endYear=endYear,
        )


    # -------------------------------------------------
    # Step 3 — Databricks Bronze Job
    # (ingest raw JSON from S3 to Delta Bronze)
    # -------------------------------------------------
    bronze_job = DatabricksRunNowOperator(
        task_id="databricks_bronze_job",
        databricks_conn_id="databricks_default",
        job_id=12345,                      # YOUR Bronze job ID
    )


    # -------------------------------------------------
    # Step 4 — Databricks Silver Job
    # (dedupe, schema clean, merge)
    # -------------------------------------------------
    silver_job = DatabricksRunNowOperator(
        task_id="databricks_silver_job",
        databricks_conn_id="databricks_default",
        job_id=12346,                      # YOUR Silver job ID
    )


    # -------------------------------------------------
    # Step 5 — Databricks Gold Job
    # (transform to final XML import format and write to S3)
    # -------------------------------------------------
    gold_job = DatabricksRunNowOperator(
        task_id="databricks_gold_job",
        databricks_conn_id="databricks_default",
        job_id=12347,                      # YOUR Gold job ID
    )


    # DAG linking:
    funder_list = prepare_funder_list(
        funderId="{{ params.funderId }}",
        funderName="{{ params.funderName }}",
    )

    dispatched = dispatch_one_funder.expand(
        funder=funder_list,
        institutionsId="{{ params.institutionsId }}",
        startYear="{{ params.startYear }}",
        endYear="{{ params.endYear }}",
    )

    # After ALL funders finish → run ETL
    dispatched >> bronze_job >> silver_job >> gold_job
