#!/usr/bin/env python3

"""Extract daily Screen Time totals from macOS knowledgeC.db to CSV."""

import argparse
import calendar
import csv
import os
import sqlite3
import sys
from datetime import date, datetime

KNOWLEDGE_DB = os.path.expanduser(
    "~/Library/Application Support/Knowledge/knowledgeC.db"
)

QUERY = """
SELECT
    date((ZOBJECT.ZSTARTDATE + 978307200), 'unixepoch', 'localtime') AS date,
    round(sum(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0, 1) AS hours
FROM
    ZOBJECT
    LEFT JOIN ZSOURCE ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
WHERE
    ZSTREAMNAME = '/app/usage'
    AND date((ZOBJECT.ZSTARTDATE + 978307200), 'unixepoch', 'localtime') BETWEEN ? AND ?
    {device_filter}
GROUP BY
    date
ORDER BY
    date
"""


def check_database():
    """Verify the database exists and is readable."""
    if not os.path.exists(KNOWLEDGE_DB):
        print(f"Could not find knowledgeC.db at {KNOWLEDGE_DB}.", file=sys.stderr)
        sys.exit(1)
    if not os.access(KNOWLEDGE_DB, os.R_OK):
        print(
            f"Cannot read {KNOWLEDGE_DB}.\n"
            "Grant Full Disk Access to your terminal app in "
            "System Settings > Privacy & Security > Full Disk Access.",
            file=sys.stderr,
        )
        sys.exit(1)


def month_range(year, month):
    """Return the first and last date strings for a given month."""
    last_day = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def query_screentime(year, month, mac_only=False):
    """Query daily screen time for a specific month."""
    device_filter = "AND ZSOURCE.ZDEVICEID IS NULL" if mac_only else ""
    query = QUERY.format(device_filter=device_filter)
    start_date, end_date = month_range(year, month)
    db_uri = f"file:{KNOWLEDGE_DB}?mode=ro"
    with sqlite3.connect(db_uri, uri=True) as con:
        rows = con.execute(query, (start_date, end_date)).fetchall()

    results = []
    for date_str, hours in rows:
        day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%a")
        results.append((date_str, day_name, hours))

    return results


def write_csv(rows, output):
    """Write rows as CSV to a file-like object."""
    writer = csv.writer(output)
    writer.writerow(["date", "day", "hours"])
    writer.writerows(rows)


def main():
    """CLI entry point."""
    today = date.today()
    if today.month == 1:
        default_month = f"{today.year - 1:04d}-12"
    else:
        default_month = f"{today.year:04d}-{today.month - 1:02d}"

    parser = argparse.ArgumentParser(
        description="Export macOS Screen Time as a daily CSV summary."
    )
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument(
        "--month",
        default=default_month,
        help="Month to export as YYYY-MM (default: previous month)",
    )
    parser.add_argument(
        "--mac-only", action="store_true", help="Exclude iOS device data"
    )
    args = parser.parse_args()

    try:
        dt = datetime.strptime(args.month, "%Y-%m")
    except ValueError:
        print(f"Invalid month format: {args.month} (expected YYYY-MM)", file=sys.stderr)
        sys.exit(1)

    check_database()
    rows = query_screentime(dt.year, dt.month, mac_only=args.mac_only)

    if not rows:
        print(f"No Screen Time data found for {args.month}.", file=sys.stderr)
        sys.exit(0)

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            write_csv(rows, f)
        print(f"Written {len(rows)} days to {args.output}", file=sys.stderr)
    else:
        write_csv(rows, sys.stdout)


if __name__ == "__main__":
    main()
