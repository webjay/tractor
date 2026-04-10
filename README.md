# Tractor

Export macOS Screen Time data as a daily CSV summary.

Reads the `knowledgeC.db` database and outputs one row per day with total hours across all devices.

## Requirements

- macOS with Screen Time enabled
- Python 3.9+
- Full Disk Access granted to your terminal app (System Settings > Privacy & Security > Full Disk Access)

To include iOS Screen Time data, enable "Share across devices" on devices signed into the same iCloud account.

## Usage

Exports the previous month by default:

```
python3 screentime.py
```

Output:

```csv
date,day,hours
2026-03-20,Fri,2.2
2026-03-22,Sun,4.6
2026-03-23,Mon,5.6
```

Export a specific month:

```
python3 screentime.py --month 2026-04
```

Write to a file:

```
python3 screentime.py -o report.csv
```

Exclude iOS devices (Mac only):

```
python3 screentime.py --mac-only
```

## Install

```
pip install .
tractor
```
