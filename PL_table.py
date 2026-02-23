import pandas as pd
import numpy as np
from sqlalchemy import create_engine
pl_table=pd.read_json(r'C:\Users\Hariharan\Desktop\MAP\data\pl_table.json',lines=True)
print(pl_table)
print(pl_table.isna().sum())

#Split by underscore
parts=pl_table["PL"].str.split("_",expand=True)
pl_table["brand_sku"]=parts[0]
pl_table["Category"]=parts[1]
pl_table["Subcategory"]=parts[2]

#Known Brands
Brands=['DELL','HP']
#Extracting Brand and SKU
def split_brand_sku(value):
    for brand in Brands:
        if value.startswith(brand):
            return pd.Series([brand, value[len(brand):]])
    return pd.Series([None, None])
             
#Extracting Brand
pl_table[["Brand","SKU"]]=pl_table["brand_sku"].apply(lambda x: split_brand_sku(x))
pl_table=pl_table.drop(columns=["brand_sku",'SKU'])
print(pl_table)

engine = create_engine("mysql+pymysql://root:123456789@localhost/map_project")
connection=engine.connect()
pl_table.to_sql("dim_pl_table", engine, if_exists="replace", index=False)
print(" PL Table transferred")