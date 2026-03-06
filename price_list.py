import pandas as pd
from sqlalchemy import create_engine
import yaml
from pathlib import Path

#File paths (edit these if needed)
BASE_DIR = Path(r"C:\Users\Hariharan\Desktop\MAP\data")

PRICE_LIST_FILE = BASE_DIR / "price list.yaml"
LPP_FILE = BASE_DIR / "LPP price logic.xlsx"

# Load price list (YAML → DataFrame)
with open(PRICE_LIST_FILE, "r") as file:
    price_list = yaml.safe_load(file)

price_list = pd.DataFrame(price_list)

# Make column names consistent
price_list.columns = price_list.columns.str.lower().str.strip()

# Split the PL column


pl_split = price_list["pl"].str.split("_", expand=True)

if pl_split.shape[1] < 3:
    raise ValueError("PL column format is invalid")

price_list["brand_sku"] = pl_split[0]
price_list["category"] = pl_split[1]
price_list["sub_category"] = pl_split[2]

# Extract brand from brand_sku
KNOWN_BRANDS = ["DELL", "HP"]

def get_brand(value):
    for brand in KNOWN_BRANDS:
        if value.startswith(brand):
            return brand
    return None

price_list["brand"] = price_list["brand_sku"].apply(get_brand)

#drop brand_sku
price_list.drop(columns="brand_sku", inplace=True)

# Normalize text
price_list["brand"] = price_list["brand"].str.upper().str.strip()
price_list["sub_category"] = price_list["sub_category"].str.strip()

# STEP 5: Load LPP logic from Excel
lpp = pd.read_excel(LPP_FILE, header=5)

# Remove unwanted columns
lpp = lpp.loc[:, ~lpp.columns.str.startswith("Unnamed")]

# Clean column names
lpp.columns = (
    lpp.columns
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
)

# STEP 6: Convert LPP table to long format
lpp_long = lpp.melt(
    id_vars=["sub_category"],
    var_name="brand",
    value_name="lpp_percent"
)

lpp_long["brand"] = lpp_long["brand"].str.upper().str.strip()
lpp_long["lpp_percent"] = pd.to_numeric(
    lpp_long["lpp_percent"],
    errors="coerce"
)

# Remove rows without a valid percentage
lpp_long = lpp_long.dropna(subset=["lpp_percent"])


#  Normalize percentages
# Convert 10 → 0.10

#if lpp_long["lpp_percent"].max() > 1:
    #lpp_long["lpp_percent"] = lpp_long["lpp_percent"] / 100
    #lpp_long["lpp_percent"]=lpp_long["lpp_percent"]*100

# Normalize sub-category values
lpp_long["sub_category"] = (
    lpp_long["sub_category"]
    .str.replace(r"^\d+\.\s*", "", regex=True)
    .replace({
        "Toner": "TON",
        "Inkjet": "INK",
        "Laserjet": "LJ"
    })
)

# STEP 9: Merge price list with LPP data
final_pricelist = price_list.merge(
    lpp_long,
    on=["brand", "sub_category"],
    how="left"
)

# Calculate LPP price
final_pricelist["lpp_price"] = (
    final_pricelist["map"] * (1 - final_pricelist["lpp_percent"])
)

# Basic validation
missing = final_pricelist["lpp_percent"].isna().sum()
if missing > 0:
    print(f"WARNING: {missing} rows are missing LPP values")

print(final_pricelist)
final_pricelist= final_pricelist[final_pricelist['lpp_percent'] != 'null']
print(final_pricelist.shape)

#('''engine = create_engine(
#    "mysql+pymysql://root:123456789@localhost/map_project"
#)
#final_pricelist.to_sql("fact_price", engine, if_exists="replace", index=False)
#print(" Price transferred")
#final_pricelist.to_csv(r"C:\Users\Hariharan\Desktop\MAP\data\final_price_list.csv", index=False)''')
final_pricelist['sku']=='6N4F1AA'