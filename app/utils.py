
from datetime import datetime, date

# Try several common formats, including your "5-Mar-29"
DATE_FORMATS = [
    "%Y-%m-%d",      # 2029-03-05
    "%m/%d/%Y",      # 03/05/2029
    "%d/%m/%Y",      # 05/03/2029
    "%d-%b-%Y",      # 05-Mar-2029
    "%d-%b-%y",      # 05-Mar-29
    "%b %d, %Y",     # Mar 5, 2029
    "%d %b %Y",      # 5 Mar 2029
]

def parse_date_loose(s: str | None) -> date | None:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            # If two-digit year parsed to the past (e.g., 1929), bump +100 to favor 2029.
            if dt.year < 1970:
                dt = dt.replace(year=dt.year + 100)
            return dt.date()
        except ValueError:
            continue
    return None

TRUE_VALUES = {"true", "yes", "y", "1", "t"}

def parse_bool_loose(s: str | None) -> int:
    """Return 1 for truthy values, else 0 (SQLite-friendly)."""
    if s is None:
        return 0
    return 1 if s.strip().lower() in TRUE_VALUES else 0
