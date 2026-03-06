import pandas as pd
import yaml
import numpy as np

# =========================================
# 1. LOAD DATA
# =========================================

df_promo_raw = pd.read_excel(
    r"C:\Users\Hariharan\Desktop\MAP\data\promotion table.xlsx",
    header=6
)

with open(r"C:\Users\Hariharan\Desktop\MAP\data\price list.yaml") as f:
    price_data = yaml.safe_load(f)

df_price = pd.DataFrame(price_data)

# =========================================
# 2. PREPARE PRICE DATA
# =========================================

df_price["Category"] = df_price["PL"].str.split("_").str[1]
df_price["SUB_CATEGORY"] = df_price["PL"].str.split("_").str[2]

Category_map = {
    "SUP": "Supply",
    "PC": "PC",
    "PH": "Print Hardware"
}

df_price["Category"] = df_price["Category"].map(Category_map)

# =========================================
# 3. DETERMINE BUSINESS SEASON (CORRECTLY)
# =========================================

today = pd.Timestamp.today()
month = today.month

if month in [11, 12, 1]:
    season = "Q1 (Nov-Jan)"
elif month in [2, 3, 4]:
    season = "Q2 (Feb-Apr)"
elif month in [5, 6, 7]:
    season = "Q3 (May-Jul)"
else:
    season = "Q4 (Aug-Oct)"

# =========================================
# 4. NORMALIZE PROMOTION TABLE
# =========================================

promo_long = df_promo_raw.melt(
    id_vars="Category",
    var_name="Season",
    value_name="Promotion"
)


# =========================================
# 5. FILTER CURRENT SEASON PROMOTIONS
# =========================================

promo_current = promo_long[promo_long["Season"] == season]

# =========================================
# 6. JOIN PROMOTIONS TO PRICE DATA
# =========================================

df = df_price.merge(
    promo_current,
    on="Category",
    how="left"
)

# =========================================
# 7. APPLY PROMOTION (ROBUST LOGIC)
# =========================================

def apply_promo(map_val, promo):
    if pd.isna(promo):
        return map_val

    promo = promo.strip()

    if "%" in promo:
        percent = float(promo.replace("%", "").split()[0])
        return round(map_val * (1 - percent / 100), 2)

    if "$" in promo:
        value = float(promo.replace("$", "").split()[0])
        return max(map_val - value, 0)

    return map_val  # Free accessories, services, etc.

df["Final_Price"] = [
    apply_promo(m, p)
    for m, p in zip(df["MAP"], df["Promotion"])
]

# =========================================
# 8. FINAL OUTPUT
# =========================================

df_final = df[[
    "PL",
    "sku",
    "Category",
    "Season",
    "Promotion",
    "MAP",
    "Final_Price"
]]

print(df_final)
df_final= df_final[df_final['Promotion'] != "Free accessories"]
df_final= df_final[df_final['Promotion'] != "Free setup service"]
print(df_final)
df_final.to_csv(r"C:\Users\Hariharan\Desktop\MAP\data\promotion_with_price.csv", index=False)
df_final["sku"]=='6N4F1AA'