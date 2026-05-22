from datetime import datetime, date

def escape_xml(text: str) -> str:
    """
    Escape special characters in a string for XML.
    """
    if text is None:
        return ""

    return (
        text.replace("&", "&amp;")   
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            # .replace('"', "&quot;")
            # .replace("'", "&apos;")
    )


def add_months(start_date, months):
    """
    Add a specified number of months to a date.
    """

    months = int(months)

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    year = start_date.year + (start_date.month - 1 + months) // 12
    month = (start_date.month - 1 + months) % 12 + 1

    return date(year, month, 1)