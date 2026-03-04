# Oracle AWR Report Generator

A Python script to connect to Oracle databases and generate AWR (Automatic Workload Repository) reports.

## Prerequisites

- Python 3.6 or higher
- Oracle Database with AWR enabled
- Database user with appropriate privileges (SELECT on DBA_HIST_* views and EXECUTE on DBMS_WORKLOAD_REPOSITORY)

## Installation

1. Install the required Python package:
```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install oracledb
```

2. If you're using Oracle Instant Client (for older Oracle databases), you may need to install it separately. For Oracle Database 12c and later, the python-oracledb package works in "Thin" mode without requiring Oracle Client libraries.

## Usage

Run the script:
```bash
python generate_awr_report.py
```

The script will prompt you for:
1. Oracle username
2. Oracle password (hidden input)
3. DSN (Data Source Name) in format: `host:port/service_name`
   - Example: `localhost:1521/ORCL`
   - Example: `dbserver.example.com:1521/PRODDB`

4. The script will display the 20 most recent snapshots
5. Enter the beginning snapshot ID
6. Enter the ending snapshot ID
7. Choose report format (HTML or Text)

## Example

```
Oracle AWR Report Generator
================================================================================
Enter Oracle username: system
Enter Oracle password: 
Enter DSN (host:port/service_name): localhost:1521/ORCL
Successfully connected to Oracle database: localhost:1521/ORCL

Most recent 20 snapshots:
--------------------------------------------------------------------------------
Snap ID    Begin Time                End Time                 
--------------------------------------------------------------------------------
1234       2024-02-09 14:00:00      2024-02-09 15:00:00      
1233       2024-02-09 13:00:00      2024-02-09 14:00:00      
...

Enter beginning snapshot ID: 1233
Enter ending snapshot ID: 1234

Report format:
1. HTML
2. Text
Choose format (1 or 2): 1

Generating AWR report...
Database ID: 1234567890
Instance Number: 1
Begin Snapshot ID: 1233
End Snapshot ID: 1234

AWR report saved to: awr_report_1233_1234_20240209_150000.html
```

## Required Database Privileges

The database user needs the following privileges:

```sql
GRANT SELECT ANY DICTIONARY TO username;
-- OR at minimum:
GRANT SELECT ON DBA_HIST_SNAPSHOT TO username;
GRANT SELECT ON DBA_HIST_DATABASE_INSTANCE TO username;
GRANT EXECUTE ON DBMS_WORKLOAD_REPOSITORY TO username;
```

## Features

- Interactive command-line interface
- Lists recent snapshots for easy selection
- Generates reports in HTML or Text format
- Automatic file naming with timestamp
- Secure password input (hidden)
- Error handling and validation

## Troubleshooting

**Connection Error:**
- Verify the DSN format is correct
- Ensure the database listener is running
- Check network connectivity to the database server

**Permission Error:**
- Ensure your user has the required privileges
- AWR must be enabled in the database

**No Snapshots Found:**
- AWR might not be configured or enabled
- Check if automatic snapshots are being taken

## Notes

- AWR snapshots are typically taken every hour by default
- You need at least two snapshots to generate a report
- The report shows database performance metrics between the two snapshots
- HTML format is recommended for better readability and interactive charts

## License

This script is provided as-is for use with Oracle databases.
