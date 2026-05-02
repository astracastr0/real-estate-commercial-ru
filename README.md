# Real Estate Data Processing Scripts

Automated pipeline for fetching, processing, and analyzing commercial real estate listings (sale & rent) from **CIAN.ru** across Moscow districts. Enriches data with Google Places, sends new listings to Bitrix CRM and Telegram, and emails daily reports.

## Features

- **Fetch listings** from CIAN API (sale & rent, commercial real estate)
- **Anti-detection**: stealth Playwright browser, cookie generation, captcha bypass
- **Proxy support**: Bright Data residential proxies (authenticated) or custom HTTP proxy
- **Process & join** sale/rent data to calculate payback period and ROI
- **Enrich** with nearby stores via Google Places API
- **Delta detection**: only new listings are sent forward (seen_ids tracking)
- **Bitrix CRM** integration: auto-create deals from new listings
- **Telegram** notifications with new listing summaries
- **Email reports** via SendGrid

---

## Project Structure
```
real-estate-scripts/
├── scripts/
│   ├── script1_get_sale_rent_offers.py  # CIAN API scraper (Playwright)
│   ├── script2_sale_readjs.py           # Parse sale JSONs to CSV
│   ├── script2_rent_readjs.py           # Parse rent JSONs to CSV
│   ├── script3_cian_join_sale_rent.py   # Join sale+rent, calc payback
│   ├── script4_google_nearby_cat.py     # Enrich with Google Places
│   ├── script5_send_to_bitrix.py        # Push new deals to Bitrix CRM
│   ├── script6_send_to_telegram.py      # Send to Telegram
│   ├── script_master.py                 # Single-area orchestrator
│   ├── script_master_all.py             # All-areas orchestrator + combine + delta
│   └── send_email_sendgrid.py           # Email report
├── requirements.txt
├── logs/                                # Execution logs
└── output/                              # Generated data (gitignored)
    ├── step1_json_data/                 # Raw JSON from CIAN
    └── CSV/                             # Processed CSVs per area
```

---

## Pipeline Flow

```
script_master_all.py
  │
  ├─ For each area (NAO, CAO, VAO, ZAO, SAO, SZAO, SVAO, UVAO, UAO, UZAO, ZelAO):
  │   └─ script_master.py
  │       ├─ script1  → fetch sale/rent JSON from CIAN API
  │       ├─ script2  → parse JSONs into CSVs
  │       ├─ script3  → join sale+rent, calculate payback
  │       └─ script4  → enrich with nearby stores (Google Places)
  │
  ├─ Combine all area CSVs
  ├─ Filter new listings (delta vs seen_ids.csv)
  ├─ Send to Bitrix CRM
  ├─ Send to Telegram
  └─ Email report via SendGrid
```

---

## Installation

### 1. Clone
```bash
git clone https://github.com/astracastr0/real-estate-scripts.git
cd real-estate-scripts
```

### 2. Install dependencies
```bash
pip3 install -r requirements.txt
playwright install chromium
```

### 3. Set environment variables
```bash
export GOOGLE_API_KEY="your-google-api-key"
export SENDGRID_API_KEY="your-sendgrid-api-key"
export BRIGHT_DATA_PROXY_PASS="your-bright-data-password"
```

---

## Usage

### Run full pipeline (all areas)
```bash
python3 scripts/script_master_all.py
```
Uses Bright Data proxy if `BRIGHT_DATA_PROXY_PASS` is set, otherwise falls back to default proxy.

### Run single area
```bash
python3 scripts/script_master.py NAO --api_key $GOOGLE_API_KEY
```

### Run single area with explicit proxy
```bash
python3 scripts/script_master.py NAO --api_key $GOOGLE_API_KEY \
  --proxy "http://user:pass@host:port"
```

### Fetch raw JSON only (no processing)
```bash
python3 scripts/script1_get_sale_rent_offers.py NAO \
  --sale_output_dir output/json_files_sale_NAO \
  --rent_output_dir output/json_files_rent_NAO \
  --proxy "http://user:pass@host:port"
```

---

## Proxy Configuration

The scraper supports two proxy modes:

| Mode | Format | When |
|------|--------|------|
| Bright Data (residential) | Auto-built from `BRIGHT_DATA_PROXY_PASS` env var | Default in `script_master_all.py` |
| Custom proxy | `--proxy http://host:port` or `--proxy http://user:pass@host:port` | Via CLI argument |

Residential proxies are recommended — datacenter IPs get blocked by CIAN.

---

## Cron (AWS Lightsail)

```bash
crontab -e
```
```
0 3 * * * cd /home/ubuntu/real-estate-scripts && BRIGHT_DATA_PROXY_PASS="xxx" GOOGLE_API_KEY="xxx" SENDGRID_API_KEY="xxx" python3 scripts/script_master_all.py >> logs/cron.log 2>&1
```

### Check logs
```bash
tail -f logs/execution.log
```

---

## Areas Covered

11 Moscow administrative districts (okrugs):

NAO, CAO, VAO, ZAO, SAO, SZAO, SVAO, UVAO, UAO, UZAO, ZelAO
