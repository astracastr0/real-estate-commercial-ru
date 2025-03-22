import pandas as pd
from geopy.distance import geodesic
import numpy as np
from datetime import datetime, timedelta

def join_sale_rent(sale_csv_path, rent_csv_path, output_csv_path):
    # Load the data from both CSV files
    sales_df = pd.read_csv(sale_csv_path, delimiter='|')
    rent_df = pd.read_csv(rent_csv_path, delimiter='|')

    # Convert `creationDate` to datetime
    sales_df['creationDate'] = pd.to_datetime(sales_df['creationDate'], errors='coerce', format='ISO8601')

    # Calculate the cutoff date for 3 months ago
    cutoff_date = datetime.now() - timedelta(days=90)

    # Apply filters to exclude specific sales records
    filtered_sales_df = sales_df[
        (sales_df['officeType'] != 'business') &
        (sales_df['layout'] != 'mixed') &
        (sales_df['creationDate'] >= cutoff_date) &
        (sales_df['buildYear'] >= 2007) &
        (sales_df['isFinished'] != 'FALSE') &
        (sales_df['isFinished'] != False) &
        (sales_df['description'].str.lower().str.contains("готовый бизнес") == False) &  # Exclude descriptions containing "готовый бизнес"
        (sales_df['description'].str.lower().str.contains("готовым арендным бизнесом") == False) & # Exclude descriptions containing "готовый бизнес"
        (sales_df['description'].str.lower().str.contains("готовым бизнесом") == False) & # Exclude descriptions containing "готовый бизнес"
        (sales_df['description'].str.lower().str.contains("арендатор") == False)  # Exclude descriptions containing "готовый бизнес"
  
  
        
    ]

    # Define a function to check if a rent offer is within 10 km of a sale offer
    def is_within_10km(sale, rent):
        coords_sale = (sale["geo_lat"], sale["geo_lng"])
        coords_rent = (rent["geo_lat"], rent["geo_lng"])
        distance = geodesic(coords_sale, coords_rent).kilometers
        return distance <= 10

    # Create a dictionary to store the rent offers for each sale offer
    sale_to_rent_offers = {}

    # Iterate through sale offers and find matching rent offers with different user IDs
    for _, sale_row in filtered_sales_df.iterrows():
        sale_id = sale_row["id"]
        rent_ids = []

        for _, rent_row in rent_df.iterrows():
            if (
                is_within_10km(sale_row, rent_row) and
                sale_row["userId"] != rent_row["userId"]
            ):
                rent_ids.append(rent_row["id"])

        sale_to_rent_offers[sale_id] = rent_ids

    # Create a new DataFrame with the results
    result_df = filtered_sales_df.copy()
    result_df["rent_offers"] = result_df["id"].map(sale_to_rent_offers)

    # Add the number of rent offers
    result_df["num_rent_offers"] = result_df["id"].apply(
        lambda sale_id: len(sale_to_rent_offers[sale_id])
    )

    # Add columns for min, max, and average "pricePerUnitAreaPerYearRur" values

    min_price_per_unit_area_per_year = result_df["id"].apply(
        lambda sale_id: min(rent_df[rent_df["id"].isin(sale_to_rent_offers.get(sale_id, []))]["pricePerUnitAreaPerYearRur"])
        if sale_to_rent_offers.get(sale_id) else np.nan
    )

    max_price_per_unit_area_per_year = result_df["id"].apply(
        lambda sale_id: max(rent_df[rent_df["id"].isin(sale_to_rent_offers[sale_id])]["pricePerUnitAreaPerYearRur"])
        if sale_to_rent_offers.get(sale_id) else np.nan
    )

    avg_price_per_unit_area_per_year = result_df["id"].apply(
        lambda sale_id: rent_df[rent_df["id"].isin(sale_to_rent_offers[sale_id])]["pricePerUnitAreaPerYearRur"].mean()
    )

    median_price_per_unit_area_per_year = result_df["id"].apply(
        lambda sale_id: np.median(rent_df[rent_df["id"].isin(sale_to_rent_offers[sale_id])]["pricePerUnitAreaPerYearRur"])
        if sale_to_rent_offers.get(sale_id) else np.nan
    )


    # Divide the values in the new columns by 12 (months)
    result_df["min_price_per_m2_month"] = min_price_per_unit_area_per_year/ 12
    result_df["max_price_per_m2_month"] = max_price_per_unit_area_per_year / 12
    result_df["avg_price_per_m2_month"] = avg_price_per_unit_area_per_year / 12
    result_df["median_price_per_m2_month"] = median_price_per_unit_area_per_year/ 12

    # Add four more columns divided by "price_per_meter"
    result_df["max_payback_months"] = (result_df["price_per_meter"] / result_df["min_price_per_m2_month"]).round(0)
    result_df["min_payback_months"] = (result_df["price_per_meter"] / result_df["max_price_per_m2_month"]).round(0)
    result_df["avg_payback_months"] = (result_df["price_per_meter"] / result_df["avg_price_per_m2_month"]).round(0)
    result_df["median_payback_months"] = (result_df["price_per_meter"] / result_df["median_price_per_m2_month"]
).round(0)
    # result_df = result_df[result_df["avg_payback_months"] <= 100]
    result_df = result_df[result_df["median_payback_months"] <= 105]


    # Save the result to a new CSV file
    result_df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"Combined data saved to {output_csv_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Join sale and rent data.')
    parser.add_argument('--sale_csv', type=str, help='Path to the sale offers CSV file')
    parser.add_argument('--rent_csv', type=str, help='Path to the rent offers CSV file')
    parser.add_argument('--output_csv', type=str, help='Path for the output combined CSV file')

    args = parser.parse_args()
    join_sale_rent(args.sale_csv, args.rent_csv, args.output_csv)
