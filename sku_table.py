import pandas as pd
# Load SKU table
sku_table = pd.read_xml(r'C:\Users\Hariharan\Desktop\MAP\data\sku table.xml')

print(sku_table)
sku_table.info()
sku_table.duplicated().sum()
