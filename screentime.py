#!/usr/bin/env python3
"""Extract daily Screen Time totals from macOS knowledgeC.db to CSV."""

import argparse
import csv
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from io import StringIO

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
    AND date((ZOBJECT.ZSTARTDATE + 978307200), 'unixepoch', 'localtime') >= date('now', '-30 days')
    {device_filter}
GROUP BY
    date
ORDER BY
    date
"""

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


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


def query_screentime(mac_only=False):
    """Query the past 30 days of daily screen time."""
    device_filter = "AND ZSOURCE.ZDEVICEID IS NULL" if mac_only else ""
    query = QUERY.format(device_filter=device_filter)
    with sqlite3.connect(KNOWLEDGE_DB) as con:
        rows = con.execute(query).fetchall()

    results = []
    for date_str, hours in rows:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = DAY_NAMES[dt.weekday()]
        results.append((date_str, day_name, hours))

    return results


def write_csv(rows, output):
    """Write rows as CSV to a file-like object."""
    writer = csv.writer(output)
    writer.writerow(["date", "day", "hours"])
    writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Export past 30 days of macOS Screen Time as CSV."
    )
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument(
        "--mac-only", action="store_true", help="Exclude iOS device data"
    )
    args = parser.parse_args()

    check_database()
    rows = query_screentime(mac_only=args.mac_only)

    if not rows:
        print("No Screen Time data found for the past 30 days.", file=sys.stderr)
        sys.exit(0)

    if args.output:
        with open(args.output, "w", newline="") as f:
            write_csv(rows, f)
        print(f"Written {len(rows)} days to {args.output}", file=sys.stderr)
    else:
        output = StringIO()
        write_csv(rows, output)
        print(output.getvalue(), end="")


if __name__ == "__main__":
    main()
