import pandas as pd
seller_mapping = pd.read_excel(r'C:\Users\Hariharan\Desktop\MAP\data\seller mapping.xlsx')
print(seller_mapping)
seller_mapping.info()
seller_mapping.duplicated()