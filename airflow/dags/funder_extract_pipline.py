from airflow import DAG
from airflow.decorators import task
from datetime import datetime
import subprocess

from main import send_grant_sqs_for_one_funder
from sideJobs.brandeis_funder import get_all_funders


def run_local_spark(script):
    """Runs a local PySpark script."""
    cmd = [
        "spark-submit",
        "--master", "local[*]",
        script
    ]
    subprocess.run(cmd, check=True)


with DAG(
    dag_id="funder_award_queue_dispatcher",
    start_date=datetime(2025, 11, 9),
    schedule_interval=None,
    catchup=False,
    tags=["funder", "sqs", "pipeline", "local_spark"],
    params={
        "funderId": None,
        "funderName": None,
        "institutionsId": "I6902469",
        "startYear": 2017,
        "endYear": 2025,
    }
):

    # ---------------------------
    # Step 1 — Determine funders
    # ---------------------------
    @task
    def prepare_funder_list(funderId, funderName):
        if funderId == "all" or funderName == "all":
            return get_all_funders()
        return [{"id": funderId, "name": funderName}]


    # ---------------------------
    # Step 2 — Dispatch per funder
    # ---------------------------
    @task
    def dispatch_one_funder(funder, institutionsId, startYear, endYear):
        return send_grant_sqs_for_one_funder(
            funderId=funder["id"],
            funderName=funder["name"],
            institutionsId=institutionsId,
            startyear=startYear,
            endYear=endYear,
        )


    # ---------------------------
    # Step 3 — Local Spark Bronze
    # ---------------------------
    @task
    def bronze_spark_task():
        run_local_spark("/opt/airflow/dags/bronze_etl.py")


    # ---------------------------
    # Step 4 — Local Spark Silver
    # ---------------------------
    @task
    def silver_spark_task():
        run_local_spark("/opt/airflow/dags/silver_etl.py")


    # ---------------------------
    # Step 5 — Local Spark Gold
    # ---------------------------
    @task
    def gold_spark_task():
        run_local_spark("/opt/airflow/dags/gold_etl.py")


    # DAG linking
    funder_list = prepare_funder_list(
        funderId="{{ params.funderId }}",
        funderName="{{ params.funderName }}",
    )

    dispatched = dispatch_one_funder.expand(
        funder=funder_list,
        institutionsId=["{{ params.institutionsId }}"],
        startYear=["{{ params.startYear }}"],
        endYear=["{{ params.endYear }}"],
    )


    # After funders → run Spark ETL
    dispatched >> bronze_spark_task() >> silver_spark_task() >> gold_spark_task()
