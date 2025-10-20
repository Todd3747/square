# Square Sales Report Script

This script generates a sales report from Square API for a specific date, tracking product sales and donations.

## Directory Structure

This script expects the following directory structure:
```
/
├── init.ini                    # Configuration file (outside repo)
├── venv/                      # Virtual environment (outside repo)
└── repo/
    └── square/
        ├── updated_sales.py   # Main script
        ├── run_updated_sales.sh  # Wrapper script
        ├── init.ini.example   # Configuration template
        └── requirements_all.txt
```

## Setup

1. **Create configuration file outside the repo:**
   ```bash
   cd ../../  # Go to scripts directory
   cp repo/square/init.ini.example init.ini
   ```

2. **Configure your Square credentials in `init.ini`:**
   - `token`: Your Square application access token from the Square Developer Dashboard
   - `location_id`: Your Square location ID (identifies which store/location to query)
   - `pasty`: The catalog variation ID for your main product (originally "pasty" but can be any product)
   - `donation`: The catalog item ID for donations in your Square catalog

3. **Set up virtual environment and install packages:**
   ```bash
   python3 -m venv ../../venv/all
   source ../../venv/all/bin/activate
   pip install -r requirements_all.txt
   deactivate
   ```

## Usage

Use the wrapper script which handles the virtual environment:

```bash
./run_updated_sales.sh 2025-10-18
```

Or run directly with Python (make sure virtual environment is activated):
```bash
./updated_sales.py 2025-10-18
```

## Finding Square IDs

To find the required IDs for your configuration:

1. **Access Token**: Create an application in the [Square Developer Dashboard](https://developer.squareup.com/apps)
2. **Location ID**: Use the Square API or check your Square Dashboard
3. **Catalog Object IDs**: Use the Square Catalog API to find item and variation IDs

## Output

The script generates a report showing:
- Date/time of each order
- Customer information (name, email, phone)
- Product quantities
- Donation amounts
- Order totals
- Summary statistics

## Security Note

Never commit your actual `init.ini` file to version control as it contains sensitive API credentials. The `init.ini.example` file is provided as a template.
