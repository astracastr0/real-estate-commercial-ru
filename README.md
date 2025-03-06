# 📌 Real Estate Data Processing Scripts

## Overview

This project automates the process of fetching, processing, and analyzing real estate sale and rent listings from **Cian**. It also enriches the data with nearby store information using the **Google Places API** and sends the final report via email.

## 🚀 Features

- **Fetch real estate listings** (sale & rent) from Cian
- **Process & clean data** into structured CSVs
- **Join sale & rent offers** to analyze investment potential
- **Enrich data** with nearby stores using Google Places API
- **Automate execution** on Oracle Cloud Free Tier VM
- **Send final report via email** daily

---

## 📁 Project Structure
```
real-estate-scripts/
├── README.md            # Project documentation
├── requirements.txt     # Required Python packages
├── scripts/
│   ├── script1_get_sale_rent_offers.py
│   ├── script2_rent_readjs.py
│   ├── script2_sale_readjs.py
│   ├── script3_cian_join_sale_rent.py
│   ├── script4_google_nearby.py
│   ├── script4_google_nearby_cat.py
│   ├── script_master.py
│   ├── script_master_all.py
│   ├── send_email.py    # Email automation script
├── config/
│   ├── areas.json       # Optional area mappings
├── data/
│   ├── sample_json/
│   ├── output_csv/
└── LICENSE
```

---

## 🛠️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/real-estate-scripts.git
cd real-estate-scripts
```

### 2️⃣ Install Dependencies
```
pip3 install -r requirements.txt
```
### 3️⃣ Set Up API Keys

Google Places API Key: Required for store enrichment.
SendGrid API Key: Required for email automation.

Store them as environment variables:
```
export GOOGLE_API_KEY="your-google-api-key"
export SENDGRID_API_KEY="your-sendgrid-api-key"
```
Or add them to a .env file:
```
GOOGLE_API_KEY=your-google-api-key
SENDGRID_API_KEY=your-sendgrid-api-key
```
### 🔥 Usage

Running a Single Area
```
python3 scripts/script_master.py NAO --api_key $GOOGLE_API_KEY
```
Running All Areas (Fully Automated Pipeline)
```
python3 scripts/script_master_all.py
```
Sending the Final Report via Email
```
python3 scripts/send_email.py
```
