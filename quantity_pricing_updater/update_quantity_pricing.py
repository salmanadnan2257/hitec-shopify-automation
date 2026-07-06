import sys

import pandas

# Usage: python update_quantity_pricing.py [stock_list.csv shopify_stock.csv]
# Without arguments, a file picker opens for each input.
if len(sys.argv) == 3:
    stock_list_path, shopify_stock_path = sys.argv[1], sys.argv[2]
else:
    from tkinter.filedialog import askopenfilename

    stock_list_path = ''
    shopify_stock_path = ''

    while stock_list_path == '':
        stock_list_path = askopenfilename(filetypes=[('Stock List CSV', '*.csv')])

    while shopify_stock_path == '':
        shopify_stock_path = askopenfilename(filetypes=[('Shopify Stock CSV', '*.csv')])

# # Get the absolute path to the directory containing the executable file
# # base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
# base_path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Read CSV files
shopify_stock = pandas.read_csv(shopify_stock_path)
stock_list = pandas.read_csv(stock_list_path)

# Divide shopify stock in default title
default_title_shopify_stock = shopify_stock[shopify_stock["Option1 Value"] == "Default Title"]
non_default_title_shopify_stock = shopify_stock[shopify_stock["Option1 Value"] != "Default Title"]

# Initialize Updated Quantity and Updated Cost in shopify stock
default_title_shopify_stock["Updated Quantity"] = 0
default_title_shopify_stock["Updated Cost"] = 0

# Processing Default Title
title_shopify_stock = default_title_shopify_stock["Title"].tolist()
for x in title_shopify_stock:
    if x in stock_list[stock_list['Brand'] == 'HI-TEC']["Item"].tolist():
        print('original', x)
        print(stock_list.loc[
                  (stock_list["Item"] == x) & (stock_list['Brand'] == 'HI-TEC'), ['Quantity', 'Average Cost']].values[
                  0])
        print('change')
        print(stock_list.loc[(stock_list["Item"] == x) & (stock_list['Brand'] == 'HI-TEC'), 'Quantity'].values)
        default_title_shopify_stock.loc[
            default_title_shopify_stock["Title"] == x, ['Updated Quantity', 'Updated Cost']] = stock_list.loc[
            (stock_list["Item"] == x) & (stock_list['Brand'] == 'HI-TEC'), ['Quantity', 'Average Cost']].values[0]

# Processing Non Default Title
title_shopify_stock = non_default_title_shopify_stock["Option1 Value"].tolist()
for x in title_shopify_stock:
    if x in stock_list[stock_list['Brand'] == 'HI-TEC']["Item"].tolist():
        non_default_title_shopify_stock.loc[
            non_default_title_shopify_stock["Option1 Value"] == x, ['Updated Quantity', 'Updated Cost']] = \
            stock_list.loc[
                (stock_list["Item"] == x) & (stock_list['Brand'] == 'HI-TEC'), ['Quantity', 'Average Cost']].values[0]

# Concatenate default and non default title
shopify_stock = pandas.concat([default_title_shopify_stock, non_default_title_shopify_stock])

# Get the path of the shopify stock
updated_file_path = shopify_stock_path.split('/')
updated_file_path[-1] = 'updated_' + updated_file_path[-1]
updated_file_path = '/'.join(updated_file_path)

# Export to CSV
shopify_stock.to_csv(updated_file_path, index=False)
