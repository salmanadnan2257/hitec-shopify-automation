import re
import tkinter as tk
from tkinter.filedialog import askopenfilename

import pandas


def on_enter(e):
    e.widget['background'] = '#4942E4'


def on_leave(e):
    e.widget['background'] = '#8696FE'


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


def convert_int_float(string):
    """Check if a string is an integer or a float"""
    try:
        num = float(string)
        return num
    except ValueError:
        pass


def open_file(filename):
    filepath = ''
    while filepath == '':
        error.config(state=tk.NORMAL)
        error.config(fg='red')
        text = f'Please select a {filename} XLSX/CSV file'
        error.delete(1.0, tk.END)
        error.insert(tk.END, text)
        error.config(state=tk.DISABLED)
        filepath = askopenfilename(filetypes=[(f'{filename} XLSX', '*.xlsx'),
                                              (F'{filename} CSV', '*.csv')])
        if filepath.split('.')[-1] == 'xlsx':
            return filepath, True
        else:
            return filepath, False


def update_quantity_and_pricing():
    stock_list_path, condition = open_file('Stock List')
    shopify_stock_path, condition2 = open_file('Shopify Stock')

    # Read XLSX/CSV files
    if condition:
        shopify_stock = pandas.read_excel(shopify_stock_path)
    else:
        shopify_stock = pandas.read_csv(shopify_stock_path)

    if condition2:
        stock_list = pandas.read_excel(stock_list_path)
    else:
        stock_list = pandas.read_csv(stock_list_path)

    # Divide shopify stock in default title
    default_title_shopify_stock = shopify_stock[shopify_stock["Option1 Value"] == "Default Title"]
    non_default_title_shopify_stock = shopify_stock[shopify_stock["Option1 Value"] != "Default Title"]

    # Initialize Updated Quantity and Updated Cost in shopify stock
    default_title_shopify_stock["Updated Quantity"] = 0
    default_title_shopify_stock["Updated Cost"] = 0

    # Convert all values that are float in Item column in stock list to float without using lambda
    stock_list['Item'] = stock_list['Item'].apply(convert_int_float)
    # string = [type(x) for x in stock_list['Item'].tolist() if type(x) != float]
    # print(len(stock_list))
    # return

    # Processing Default Title
    title_shopify_stock = default_title_shopify_stock["Title"].tolist()
    for x in title_shopify_stock:
        if x in stock_list[stock_list['Brand'] == 'HI-TEC']["Item"].tolist():
            print('original', x)
            print(stock_list.loc[
                      (stock_list["Item"] == x) & (stock_list['Brand'] == 'HI-TEC'), ['Quantity',
                                                                                      'Average Cost']].values[
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
                    (stock_list["Item"] == x) & (stock_list['Brand'] == 'HI-TEC'), ['Quantity', 'Average Cost']].values[
                    0]

    # Concatenate default and non default title
    shopify_stock = pandas.concat([default_title_shopify_stock, non_default_title_shopify_stock])

    # Convert Updated Quantity and Updated Cost to float
    shopify_stock['Updated Quantity'] = shopify_stock['Updated Quantity'].astype(float)
    shopify_stock['Updated Cost'] = shopify_stock['Updated Cost'].astype(float)

    # # Replace values with 0 to NaN in Updated Quantity and Updated Cost
    # shopify_stock['Updated Quantity'] = shopify_stock['Updated Quantity'].replace(0, pandas.np.nan)
    # shopify_stock['Updated Cost'] = shopify_stock['Updated Cost'].replace(0, pandas.np.nan)

    # Get the path of the shopify stock
    updated_file_path = shopify_stock_path.split('/')
    updated_file_path[-1] = 'updated_p_' + updated_file_path[-1]
    updated_file_path = '/'.join(updated_file_path)

    # Convert extension to XLSX
    updated_file_path = updated_file_path.split('.')
    updated_file_path[-1] = 'xlsx'
    updated_file_path = '.'.join(updated_file_path)

    # Save the updated shopify stock
    message = 'Quantity and Pricing has been updated!'
    save_data(updated_file_path=updated_file_path, message=message, df=shopify_stock)


def extract_data_from_html():
    # # Get the absolute path to the directory containing the executable file
    # # base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # base_path = os.path.abspath(os.path.dirname(sys.argv[0]))

    shopify_stock_path, condition = open_file('Shopify Stock')

    # Read XLSX/CSV files
    if condition:
        df = pandas.read_excel(shopify_stock_path)
    else:
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
                    df[value][x[0]] = float(text[index])
            elif value == 'width':
                print('check width', 'total width' in text)
                if 'total width' in text:
                    index = text.index('total width') + 1
                    if check_int_float(text[index]):
                        overall_dimensions += f'{value}: {text[index]}\n'
                        df[value][x[0]] = float(text[index])
            else:
                for temp in text:
                    if value in temp:
                        index = text.index(temp) + 1
                        if check_int_float(text[index]):
                            overall_dimensions += f'{value}: {text[index]}\n'
                            df[value][x[0]] = float(text[index])
        print(overall_dimensions)
        print('----------------------------------------')

    # Get the path of the shopify stock
    updated_file_path = shopify_stock_path.split('/')
    updated_file_path[-1] = 'updated_h_' + updated_file_path[-1]
    updated_file_path = '/'.join(updated_file_path)

    # Convert extension to XLSX
    updated_file_path = updated_file_path.split('.')
    updated_file_path[-1] = 'xlsx'
    updated_file_path = '.'.join(updated_file_path)

    # Save the dataframe to a CSV file
    message = 'Dimensions has been successfully updated!'
    save_data(updated_file_path=updated_file_path, message=message, df=df)


def variants_detection():
    shopify_stock_path, condition = open_file('Shopify Stock')

    # Read XLSX/CSV file
    if condition:
        df = pandas.read_excel(shopify_stock_path)
    else:
        df = pandas.read_csv(shopify_stock_path)

    # Add columns Bore, Cage, and Seal Type
    df['Bore'] = ""
    df['Cage'] = ""
    df['Seal Type'] = ""

    # Divide df into 2 dataframes (default title and non default title)
    # default_title_shopify_stock = df[df['Option1 Value'] == 'Default Title']
    non_default_title_shopify_stock = df[df['Option1 Value'] != 'Default Title']['Option1 Value'].tolist()

    # Initialize bore diameter, outside diameter and width
    bore_possible_variants = ['k']
    bore_possible_variants_name = ['Tapered']

    cage_possible_variants = ['e', 'f', 'm', 'ecp', 'ca', 'mb', 'cc']
    cage_possible_variants_name = ['Steel', 'Fibre', 'Brass', 'Polyamide', 'Brass', 'Steel', 'Brass']

    sealtype_possible_variants = ['2rs', 'rs', 'z', '2z']
    sealtype_possible_variants_name = ['2RS', 'rs', 'z', '2z']

    # for item in non_default_title_shopify_stock['Option1 Value'].tolist():
    for item in non_default_title_shopify_stock:
        # Check Bore
        item_individual = item.lower().split()

        if check_int_float(item_individual[-1]):
            df.loc[df['Option1 Value'] == item, 'Bore'] = 'Plain'
            df.loc[df['Option1 Value'] == item, 'Cage'] = 'Steel'
            if item_individual[0][0] == '2' and len(item_individual[0]) == 5:
                df.loc[df['Option1 Value'] == item, 'Cage'] = 'Brass'
        else:
            x = 0
            for value in item_individual:
                if check_int_float(value):
                    x = item_individual.index(value)
                print(df.loc[df['Option1 Value'] == item, 'Bore'])
                if value in bore_possible_variants:
                    print(value, value in bore_possible_variants, 'bore')
                    index = bore_possible_variants.index(value)
                    df.loc[df['Option1 Value'] == item, 'Bore'] = bore_possible_variants_name[index]

                if value in cage_possible_variants:
                    print(value, value in cage_possible_variants, 'cage')
                    index = cage_possible_variants.index(value)
                    df.loc[df['Option1 Value'] == item, 'Cage'] = cage_possible_variants_name[index]

                if value in sealtype_possible_variants:
                    print(value, value in sealtype_possible_variants, 'sealtype')
                    index = sealtype_possible_variants.index(value)
                    df.loc[df['Option1 Value'] == item, 'Seal Type'] = sealtype_possible_variants_name[
                        index]

            if 'e' in item_individual or 'ca' in item_individual or 'mb' in item_individual:
                if item_individual[x][0] == '2' and len(item_individual[x]) == 5:
                    df.loc[df['Option1 Value'] == item, 'Cage'] = 'Brass'
            if 'cc' in item_individual:
                if item_individual[x][0] == '2' and len(item_individual[x]) == 5:
                    df.loc[df['Option1 Value'] == item, 'Cage'] = 'Steel'

    # Get the path of the shopify stock
    updated_file_path = shopify_stock_path.split('/')
    updated_file_path[-1] = 'updated_v_' + updated_file_path[-1]
    updated_file_path = '/'.join(updated_file_path)

    # Convert extension to XLSX
    updated_file_path = updated_file_path.split('.')
    updated_file_path[-1] = 'xlsx'
    updated_file_path = '.'.join(updated_file_path)

    # Save the dataframe to a CSV file
    message = 'Variants has been successfully updated!'
    save_data(updated_file_path=updated_file_path, message=message, df=df)


def save_data(updated_file_path, message, df):
    is_file_found = False
    counter = 0
    name = updated_file_path.split('/')[-1].split('.')[:-1]
    name = '.'.join(name)
    print(name)
    while not is_file_found:
        # Check if the file exists
        try:
            pandas.read_excel(updated_file_path)
            counter += 1
            updated_file_path = updated_file_path.split('/')[:-1]
            updated_file_path = '/'.join(updated_file_path) + f'/({counter}){name}.xlsx'
        except FileNotFoundError:
            # If it doesn't exist, save the file
            print('entered')
            df.to_excel(updated_file_path, index=False)
            # error.config()
            text = f'{message}\nFile saved at {updated_file_path}'
            error.config(state=tk.NORMAL)
            error.delete(1.0, tk.END)
            error.config(fg='green')
            error.insert(tk.END, text, 'green')
            error.config(state=tk.DISABLED)
            is_file_found = True


root = tk.Tk()
root.config(bg='#E6FFFD')
root.title('Shopify Stock Updater')
root.geometry('900x800')
root.resizable(False, False)

# Title
title = tk.Label(root, text="Shopify Stock Updater", font=("Arial", 30), bg="#E6FFFD", fg="#B799FF")
title.place(relx=0.5, rely=0.1, anchor="center")

# Label
label = tk.Label(root, text="Choose an option:", font=("Arial", 20), bg="#E6FFFD", fg="#B799FF")
label.place(relx=0.5, rely=0.3, anchor="center")

# Update Quantity and Pricing Button
update_quantity_pricing = tk.Button(root, text="Update Quantity and Pricing", font=("Arial", 20), bg="#8696FE",
                                    fg="#E6FFFD", activebackground="#11009E", activeforeground="#E6FFFD", bd=0,
                                    command=update_quantity_and_pricing)
update_quantity_pricing.place(relx=0.5, rely=0.4, anchor="center")
update_quantity_pricing.bind("<Enter>", on_enter)
update_quantity_pricing.bind("<Leave>", on_leave)

# Extract Data from HTML Button
extract_data_html = tk.Button(root, text="Extract Data from HTML", font=("Arial", 20), bg="#8696FE",
                              fg="#E6FFFD", activebackground="#11009E", activeforeground="#E6FFFD", bd=0,
                              command=extract_data_from_html)
extract_data_html.place(relx=0.5, rely=0.5, anchor="center")
extract_data_html.bind("<Enter>", on_enter)
extract_data_html.bind("<Leave>", on_leave)

# Variant Column Adding Button
variant_detection = tk.Button(root, text="Variant Detection", font=("Arial", 20), bg="#8696FE",
                              fg="#E6FFFD", activebackground="#11009E", activeforeground="#E6FFFD", bd=0,
                              command=variants_detection)
variant_detection.place(relx=0.5, rely=0.6, anchor="center")
variant_detection.bind("<Enter>", on_enter)
variant_detection.bind("<Leave>", on_leave)

# Error Textbox
error = tk.Text(root, height=6, width=70, font=("Arial", 15), bg="white", fg="red")
error.place(relx=0.5, rely=0.75, anchor="center")
error.config(state=tk.DISABLED)

# Mainloop
root.mainloop()
