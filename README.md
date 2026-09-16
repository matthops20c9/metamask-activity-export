# metamask-activity-export

I needed a way to get my complete transaction history out of MetaMask for tax purposes and self-hosted backup. The browser extension UI doesn't allow exporting a single, unified CSV of all activities across different networks and accounts at once. 

This tool parses the raw MetaMask State Log JSON file and exports a clean, flat list of all transactions, including internal state transitions, gas costs, and status codes.

## How to get your state log

1. Open MetaMask in your browser.
2. Go to Settings -> Advanced.
3. Scroll down to "Download State Log" and save the JSON file.

## Installation

Clone the repository and install the dependencies:

```cmd
pip install -r requirements.txt
```

## Running the exporter

Run the script against your downloaded state log:

```cmd
python export.py C:\Users\User\Downloads\state-log.json --output history.csv
```

By default, it exports to CSV. You can also export to JSON or dump a quick summary directly to your terminal:

```cmd
python export.py state-log.json --format terminal
```

Options:
* `--output, -o`: Path to save the output file (optional for terminal format).
* `--format, -f`: Output format (`csv`, `json`, or `terminal`). Defaults to `csv`.
* `--network`: Filter transactions by chain ID (e.g., `1` for Ethereum, `137` for Polygon).

<!-- last-checked: 2026-09-16 -->
