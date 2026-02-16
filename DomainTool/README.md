# DomainTool

A comprehensive Python-based domain analysis tool for performing various network lookups and gathering domain information. Perfect for auditing domain portfolios, security assessments, and network reconnaissance.

## Features

### Network Lookups
- **WHOIS Lookup** - Extract registrar, name servers, and registration details
- **NSLookup** - Query name server records
- **DNS Lookup** - Resolve domain DNS records
- **Reverse DNS Lookup** - Find hostnames from IP addresses
- **SSL Certificate Lookup** - Check SSL certificate details and expiration
- **HTTP Headers Lookup** - Examine HTTP response headers

### Data Management
- **Multiple Input Formats** - Excel (.xlsx), XML, Text (.txt), or manual terminal entry
- **Multiple Output Formats** - Save results as Excel, XML, Text, or print to terminal
- **Batch Processing** - Process multiple domains in one operation
- **Interactive Menu System** - User-friendly command-line interface

## Installation

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Required Dependencies

```bash
pip install openpyxl python-whois dnspython pyOpenSSL requests
```

Or install from requirements file:

```bash
pip install -r requirements.txt
```

### Dependencies List
- `openpyxl` - Excel file operations
- `python-whois` - WHOIS lookups
- `dnspython` - DNS operations
- `pyOpenSSL` - SSL certificate handling
- `requests` - HTTP operations
- `tkinter` - File dialog (usually comes with Python)

## Usage

### Starting the Application

```bash
python domainTool.py
```

### Main Menu Options

```
1. Load data from Excel
2. Load data from XML
3. Load data from Text
4. Load data from Terminal
5. Exit
```

### Input File Formats

#### Excel (.xlsx)
Domains should be in the first column:
```
domain.com
example.org
website.net
```

#### XML
```xml
<?xml version="1.0"?>
<root>
    <domain>domain.com</domain>
    <domain>example.org</domain>
    <domain>website.net</domain>
</root>
```

#### Text (.txt)
One domain per line:
```
domain.com
example.org
website.net
```

#### Terminal Input
Enter domains directly when prompted, one per line. Press Enter twice when done.

### Function Menu

After loading data, select lookup operations:

```
1. Perform WHOIS lookup
2. Perform NSLookup
3. Perform DNS lookup
4. Perform reverse DNS lookup
5. Perform SSL certificate lookup
6. Perform HTTP headers lookup
7. Return to Main Menu
8. Exit
```

**Pro Tip:** You can select multiple operations by entering comma-separated numbers (e.g., `1,2,3`)

### WHOIS Lookup Output

The WHOIS lookup extracts:
- **Domain name**
- **Registrar** (e.g., GoDaddy, Namecheap, MarkMonitor)
- **Creation Date**
- **Expiration Date**
- **Name Servers**
- **Status** (success/error)
- **Error Message** (if lookup failed)

**Excel Output Format:**
| Domain | Registrar | Creation Date | Expiration Date | Name Servers | Status | Error Message |
|--------|-----------|---------------|-----------------|--------------|---------|---------------|
| example.com | GoDaddy.com, LLC | 2015-03-15 | 2026-03-15 | ns1.godaddy.com, ns2.godaddy.com | success | |
| google.com | MarkMonitor Inc. | 1997-09-15 | 2028-09-14 | ns1.google.com, ns2.google.com | success | |

**Text/Terminal Output Format:**
```
[1] Domain: example.com
Registrar: GoDaddy.com, LLC
Creation Date: 2015-03-15
Expiration Date: 2026-03-15
Name Servers: ns1.godaddy.com, ns2.godaddy.com
------------------------------------------------------------
```

### Save Menu

After running lookups, choose how to save results:

```
1. Save output as Excel
2. Save output as XML
3. Save output as Text
4. Print output to Terminal
5. Return to Main Menu
6. Exit
```

## Output Formats

### Excel Format (Recommended for Analysis)

All lookups save as **structured columns** for easy sorting, filtering, and analysis:

**Features:**
- One row per domain/IP
- Separate columns for each data field
- Colored headers (blue background, white text)
- Auto-adjusted column widths
- Status column to identify failed lookups
- Error messages for troubleshooting

**Example - WHOIS Results:**
- Columns: Domain | Registrar | Creation Date | Expiration Date | Name Servers | Status | Error Message

**Why use Excel format:**
- Sort by registrar to group domains
- Filter by expiration date to find domains expiring soon
- Count domains per registrar with pivot tables
- Import into other tools (Tableau, Power BI)

### Text Format (Readable Output)

Saves as human-readable text with numbered entries:
```
[1] Domain: example.com
Registrar: GoDaddy.com, LLC
Creation Date: 2015-03-15
Expiration Date: 2026-03-15
Name Servers: ns1.godaddy.com, ns2.godaddy.com
------------------------------------------------------------
[2] Domain: google.com
...
```

### XML Format (Machine-Readable)

Structured XML with nested elements:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<results>
    <result>
        <domain>example.com</domain>
        <registrar>GoDaddy.com, LLC</registrar>
        <creation_date>2015-03-15</creation_date>
        ...
    </result>
</results>
```

### Terminal Output

Same as text format but displayed in the console with separators for easy reading.

## Workflow Examples

### Example 1: Audit Domain Registrars from Excel

1. Run `python domainTool.py`
2. Select `1` (Load data from Excel)
3. Choose your .xlsx file with domains
4. Select `1` (Perform WHOIS lookup)
5. Select `1` (Save output as Excel)
6. Choose save location

### Example 2: Quick DNS Check from Terminal

1. Run `python domainTool.py`
2. Select `4` (Load data from Terminal)
3. Enter domains, press Enter twice when done
4. Select `3` (Perform DNS lookup)
5. Select `4` (Print output to Terminal)

### Example 3: Multiple Lookups on Same Data

1. Load data (any method)
2. Select `1,2,3` to perform WHOIS, NS, and DNS lookups simultaneously
3. Save results in preferred format

## Project Structure

```
DomainTool/
├── domainTool.py           # Main entry point
├── data_processor.py       # Core data processing logic
├── menu.py                 # Menu initialization
├── menu_logic.py           # Menu flow and user interaction
├── file_operations.py      # File I/O operations
├── network_operations.py   # Network lookup implementations
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

## Module Descriptions

### `domainTool.py`
Main application entry point that initializes the DataProcessor and starts the menu system.

### `data_processor.py`
Core class that manages data lifecycle:
- Loading data from various sources
- Storing lookup results
- Coordinating between file operations and network operations

### `menu_logic.py`
Handles all menu interactions:
- Main menu for data loading
- Function menu for selecting lookups
- Save menu for output options

### `file_operations.py`
Manages all file I/O:
- Loading from Excel, XML, Text
- Saving to Excel, XML, Text
- Terminal input/output
- File dialog interactions

### `network_operations.py`
Implements all network lookup functions:
- WHOIS queries
- DNS operations
- SSL certificate checks
- HTTP header inspection

## Common Use Cases

### Domain Portfolio Audit
Use WHOIS lookup to map all domains to their registrars for inventory purposes. The structured Excel output makes it easy to:
- Group domains by registrar
- Count how many domains are with each registrar
- Identify consolidation opportunities

### Expiration Tracking
1. Run WHOIS lookup on your domain portfolio
2. Save as Excel
3. Sort by "Expiration Date" column
4. Filter to show domains expiring in the next 90 days
5. Create renewal reminders

### Registrar Cost Analysis
1. Export WHOIS data to Excel
2. Add a "Cost" column for each registrar's pricing
3. Use pivot tables to calculate total costs per registrar
4. Identify opportunities to consolidate and save money

### Security Assessment
Combine SSL certificate lookup with HTTP headers to assess security configurations. Excel format allows you to:
- Sort by SSL expiration date
- Filter domains missing security headers
- Track certificate renewal schedules

### DNS Troubleshooting
Use NSLookup and DNS lookup to verify proper DNS configuration. The structured output helps you:
- Quickly identify misconfigured domains
- Compare name servers across your portfolio
- Spot DNS propagation issues

## Tips and Best Practices

### For Large Domain Lists (100+ domains)

1. **Be mindful of rate limits** - WHOIS servers may throttle or block excessive queries
2. **Run during off-peak hours** - Better success rates
3. **Save intermediate results** - Save after each batch
4. **Handle errors gracefully** - Review failed lookups and retry manually if needed

### WHOIS Lookup Limitations

- Some registrars limit query frequency
- Different TLDs may return different data formats
- Privacy protection services may hide registrar details
- Temporary network issues can cause failures

### Input Data Tips

- Remove duplicates before processing
- Ensure proper domain format (no http://, no paths)
- For SSL lookups, ensure domains are accessible on port 443
- For HTTP headers, domains should be web-accessible

## Troubleshooting

### "Failed to load data from Excel file"
- Verify file is .xlsx format
- Check that domains are in the first column
- Ensure file isn't corrupted or password-protected

### "WHOIS lookup failed"
- Domain may not exist or is improperly formatted
- WHOIS server may be temporarily unavailable
- Rate limiting may be in effect - try again later

### "SSL certificate lookup failed"
- Domain may not have SSL certificate
- Port 443 may be blocked
- Certificate may be expired or invalid

### "No file selected"
- File dialog was canceled
- Permission issues with file location
- Try running with appropriate permissions

## Security Considerations

- WHOIS queries are logged by registrars
- Be respectful of rate limits to avoid IP blocking
- Some lookups may trigger security monitoring
- Use responsibly and only on domains you own or have permission to query
