# Tractor

Export  Screen Time data as a daily CSV summary.

Reads the `knowledgeC.db` database and outputs one row per day with total hours across all devices.

## Requirements

- macOS with Screen Time enabled
- Python 3.9+
- Full Disk Access granted to your terminal app (System Settings > Privacy & Security > Full Disk Access)

To include iOS Screen Time data, enable "Share across devices" on devices signed into the same iCloud account.

## Usage

```
python3 screentime.py
```

Output:

```csv
date,day,hours
2026-04-10,Thu,8.3
2026-04-09,Wed,7.1
```

Write to a file:

```
python3 screentime.py -o report.csv
```

## Install

```
pip install .
tractor
```
