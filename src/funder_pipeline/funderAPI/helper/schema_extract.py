import csv
from pathlib import Path
from typing import Optional
from datetime import datetime, date
from pathlib import Path


def get_grant_status_from_end_date(endDate: Optional[str]) -> str:
    """
    Returns:
      - "HISTORY" if endDate (format: "2025-month-date", i.e., "%Y-%m-%d") is before today
      - "ACTIVE" otherwise

    Notes:
      - If endDate is None/empty, treats it as "ACTIVE".
      - Raises ValueError if the date string is not in "%Y-%m-%d" format.
    """
    if not endDate:
        return "ACTIVE"
    
    if isinstance(endDate, str):
        target_date = datetime.strptime(endDate, "%Y-%m-%d").date()
    elif isinstance(endDate, date):
        target_date = endDate
    else:
        raise TypeError("endDate must be str or datetime.date")

    return "HISTORY" if target_date < date.today() else "ACTIVE"

RESOURCE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "resources"
    / "funder_41Code.csv"
)

def get_matched_funder_code(
    funder_name: str,
    csv_path: str | Path = RESOURCE_PATH,
    *,
    name_col: str = "unique_funder",
    code_col: str = "matched_funder_code",
) -> Optional[str]:
    """
    Look up `funder_name` in `csv_path` and return the corresponding matched funder code.
    Returns None if not found.
    """
    csv_path = Path(csv_path)

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get(name_col).lower() == funder_name.lower():
                return row.get(code_col)

    return None