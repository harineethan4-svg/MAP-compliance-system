import pandas as pd
import glob
import os

# CONFIGURATION

BASE_PATH = r"C:\Users\Hariharan\Desktop\MAP\data"
SELLER_DATA_PATH = r"C:\Users\Hariharan\Desktop\MAP\Seller Data"
OUTPUT_PATH = r"C:\Users\Hariharan\Desktop\MAP\warnings"
os.makedirs(OUTPUT_PATH, exist_ok=True)

# UTILITY FUNCTIONS
def normalize_columns(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

def generate_warning_letter(seller, sku, pl, lpp_price, advertised_price):
    return f"""Subject: MAP Policy Violation Warning

Dear {seller},

We have identified a violation of the Minimum Advertising Price (MAP) policy.

Violation details:
- SKU: {sku}
- PL Code: {pl}
- Lowest Permissible Price (LPP): {lpp_price}
- Advertised Price: {advertised_price}

Please correct this violation immediately to avoid further action,
including potential suspension of selling privileges.

Regards,
Compliance Team
"""

# LOAD REFERENCE DATA
final_price_list = pd.read_csv(f"{BASE_PATH}/final_price_list.csv")
promotion_with_price = pd.read_csv(f"{BASE_PATH}/promotion_with_price.csv")
pl_table = pd.read_csv(f"{BASE_PATH}/pl_table.csv")
seller_mapping = pd.read_excel(f"{BASE_PATH}/seller mapping.xlsx")

# Normalize all reference tables
final_price_list = normalize_columns(final_price_list)
promotion_with_price = normalize_columns(promotion_with_price)
pl_table = normalize_columns(pl_table)
seller_mapping = normalize_columns(seller_mapping)

# PREPARE PROMOTIONAL PRICES
promo_prices = (
    promotion_with_price[['sku', 'final_price']]
    .dropna(subset=['final_price'])
    .drop_duplicates(subset=['sku'])
)

# BUILD AUTHORITATIVE PRICE TABLE
final_price_enriched = final_price_list.merge(
    promo_prices,
    on='sku',
    how='left'
)

# Effective LPP: promo price overrides MAP if present
final_price_enriched['lpp_price'] = (
    final_price_enriched['final_price'] # Changed 'promo_price' to 'final_price'
    .fillna(final_price_enriched['map'])
)

# PROCESS DAILY SELLER FILES

daily_files = glob.glob(os.path.join(SELLER_DATA_PATH, "2025-12-*.csv"))

if not daily_files:
    print("⚠️ No daily transaction files found.")
else:
    for file in daily_files:
        print(f"Processing: {os.path.basename(file)}")

        daily_data = pd.read_csv(file)
        daily_data = normalize_columns(daily_data)

        # Required columns check (fail fast)
        required_cols = {'sku', 'adv_price'}
        if not required_cols.issubset(daily_data.columns):
            raise ValueError(
                f"Missing required columns {required_cols} in {file}"
            )

        # Normalize pricing column
        daily_data.rename(columns={'adv_price': 'price'}, inplace=True)

        # Merge authoritative LPP pricing
        daily_data = daily_data.merge(
            final_price_enriched[['sku', 'pl', 'lpp_price']],
            on='sku',
            how='left'
        )

        # DETECT MAP VIOLATIONS
        
        violations = daily_data[
            daily_data['price'].notna() &
            daily_data['lpp_price'].notna() &
            (daily_data['price'] < daily_data['lpp_price'])
        ].copy()

        if violations.empty:
            print("ℹ️ No violations found.")
            continue

        # =================================================
        # ENRICH VIOLATIONS WITH PL / SELLER INFO
        # =================================================
        violations = violations.merge(
            pl_table,
            on=['sku', 'pl'],
            how='left'
        )

        violations = violations.merge(
            seller_mapping,
            left_on='brand',
            right_on='homologated_sellers',
            how='left'
        )

        # =================================================
        # GENERATE WARNING LETTERS
        # =================================================
        for _, row in violations.iterrows():
            seller = row.get('homologated_sellers', 'Unknown Seller')

            letter = generate_warning_letter(
                seller=seller,
                sku=row['sku'],
                pl=row['pl'],
                lpp_price=row['lpp_price'],
                advertised_price=row['price']
            )

            filename = f"warning_{row['sku']}_{os.path.basename(file)}.txt"
            with open(os.path.join(OUTPUT_PATH, filename), "w", encoding="utf-8") as f:
                f.write(letter)

        print(f"⚠️ Warnings generated: {len(violations)}")