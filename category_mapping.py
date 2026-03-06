import pandas as pd

# load category mapping file
category_mapping=pd.read_json(r'C:\Users\Hariharan\Desktop\MAP\data\category mapping.json',lines=True)
print(category_mapping)
#Split by underscore
parts=category_mapping["PL"].str.split("_",expand=True)
category_mapping["brand_sku"]=parts[0]
category_mapping["Category"]=parts[1]
category_mapping["Subcategory"]=parts[2]

#Known Brands
Brands=['DELL','HP']
#Extracting Brand and SKU
def split_brand_sku(value):
    for brand in Brands:
        if value.startswith(brand):
            return pd.Series([brand, value[len(brand):]])
    return pd.Series([None, None])
             
#Extracting Brand
category_mapping[["Brand","SKU"]]=category_mapping["brand_sku"].apply(lambda x: split_brand_sku(x))
category_mapping=category_mapping.drop(columns=["brand_sku",'SKU','Brand','PL'])
print(category_mapping)