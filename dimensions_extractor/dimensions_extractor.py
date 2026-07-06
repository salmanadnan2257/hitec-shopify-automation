import re
import sys

import pandas


def remove_html_tags(text_to_be_cleaned):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text_to_be_cleaned)


def check_int_float(string):
    """Check if a string is an integer or a float"""
    try:
        float(string)
        return True
    except ValueError:
        return False


# # Get the absolute path to the directory containing the executable file
# # base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
# base_path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Usage: python dimensions_extractor.py [shopify_stock.csv]
# Without an argument, a file picker opens.
if len(sys.argv) == 2:
    shopify_stock_path = sys.argv[1]
else:
    from tkinter.filedialog import askopenfilename

    shopify_stock_path = ''

    while shopify_stock_path == '':
        shopify_stock_path = askopenfilename(filetypes=[('Shopify Stock CSV', '*.csv')])

# Read CSV files
df = pandas.read_csv(shopify_stock_path)

# Drop rows with empty values in column 'Body (HTML)'
df = df.dropna(subset=['Body (HTML)'])

# Initialize bore diameter, outside diameter and width
df['bore diameter'] = ""
df['outside diameter'] = ""
df['width'] = ""

values_to_check = ['outside diameter', 'bore diameter', 'width']
for x in df.iterrows():
    overall_dimensions = ""
    temp = str(x[1]['Body (HTML)']).lower()
    text = [x for x in remove_html_tags(temp).split('\n') if x != '']
    for value in values_to_check:
        if value in text:
            index = text.index(value) + 1
            if check_int_float(text[index]):
                overall_dimensions += f'{value}: {text[index]}\n'
                df[value][x[0]] = text[index]
        elif value == 'width':
            print('check width', 'total width' in text)
            if 'total width' in text:
                index = text.index('total width') + 1
                if check_int_float(text[index]):
                    overall_dimensions += f'{value}: {text[index]}\n'
                    df[value][x[0]] = text[index]
        else:
            for temp in text:
                if value in temp:
                    index = text.index(temp) + 1
                    if check_int_float(text[index]):
                        overall_dimensions += f'{value}: {text[index]}\n'
                        df[value][x[0]] = text[index]
    print(overall_dimensions)
    print('----------------------------------------')

# Get the path of the shopify stock
updated_file_path = shopify_stock_path.split('/')
updated_file_path[-1] = 'updated_' + updated_file_path[-1]
updated_file_path = '/'.join(updated_file_path)

# Save the dataframe to a CSV file
df.to_csv(updated_file_path, index=False)
