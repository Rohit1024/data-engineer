"""Tiny row-processing example for Airflow 2.11; no external services."""
from datetime import timedelta
import logging

import pendulum
from airflow.decorators import dag, task


@dag(
    dag_id="lab_row_taskflow",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(seconds=30)},
    tags=["lesson-0039", "taskflow"],
)
def row_taskflow():
    @task
    def sample_rows():
        return [
            {"order_id": 101, "amount_cents": 2500, "status": "paid"},
            {"order_id": 102, "amount_cents": 4200, "status": "paid"},
            {"order_id": 103, "amount_cents": 1800, "status": "cancelled"},
        ]

    @task
    def summarize(rows):
        for row in rows:
            if row["amount_cents"] < 0:
                raise ValueError(f"Negative amount for order {row['order_id']}")
        paid = [row for row in rows if row["status"] == "paid"]
        return {"paid_orders": len(paid), "paid_cents": sum(r["amount_cents"] for r in paid)}

    @task
    def verify(summary):
        if summary != {"paid_orders": 2, "paid_cents": 6700}:
            raise ValueError(f"Unexpected sample result: {summary}")
        logging.info("Verified sample: %s", summary)

    verify(summarize(sample_rows()))


row_taskflow()
