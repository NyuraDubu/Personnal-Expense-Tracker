import os
import csv
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

file_name = 'expenses.csv'
BASE_CURRENCY = 'EUR'
currency_symbol = '€'

# Add headers if the file is empty or missing
if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Amount", "Description", "Transaction Date"])

# Translations for English and French
translations = {
    'en': {
        'title': 'Expenses Tracker',
        'date': 'Date (YYYY-MM-DD)',
        'category': 'Category',
        'amount': 'Amount (in EUR)',
        'description': 'Description',
        'transaction_date': 'Transaction Date (YYYY-MM-DD)',
        'add_expense': 'Add',
        'delete_expense': 'Delete',
        'modify_expense': 'Modify',
        'save_expense': 'Save',
        'search': 'Search',
        'select_column': 'Select Column',
        'error': 'Error',
        'error_select': 'Please select an expense!',
        'total_amount': 'Total Amount: ',
        'currency': 'Currency',
        'language': 'Select Language'
    },
    'fr': {
        'title': 'Suivi des Dépenses',
        'date': 'Date (AAAA-MM-JJ)',
        'category': 'Catégorie',
        'amount': 'Montant (en EUR)',
        'description': 'Description',
        'transaction_date': 'Date de la transaction (AAAA-MM-JJ)',
        'add_expense': 'Ajouter',
        'delete_expense': 'Supprimer',
        'modify_expense': 'Modifier',
        'save_expense': 'Sauvegarder',
        'search': 'Rechercher',
        'select_column': 'Sélectionner Colonne',
        'error': 'Erreur',
        'error_select': 'Veuillez sélectionner une dépense!',
        'total_amount': 'Montant Total: ',
        'currency': 'Devise',
        'language': 'Choisir la Langue'
    }
}

current_language = 'en'
sort_descending = False

# ==============================================================================================================================================================================

def search_expenses(tree, total_amount_label, search_entry, search_column):
    search_term = search_entry.get().lower()
    column = search_column.get()

    df = view_expenses()

    if column == translations[current_language]['date']:
        filtered_df = df[df['Date'].str.contains(search_term, case=False)]
    elif column == translations[current_language]['category']:
        filtered_df = df[df['Category'].str.contains(search_term, case=False)]
    elif column == translations[current_language]['amount']:
        filtered_df = df[df['Amount'].astype(str).str.contains(search_term)]
    elif column == translations[current_language]['description']:
        filtered_df = df[df['Description'].str.contains(search_term, case=False)]
    elif column == translations[current_language]['transaction_date']:
        filtered_df = df[df['Transaction Date'].str.contains(search_term, case=False)]
    else:
        filtered_df = df

    update_table(tree, filtered_df, total_amount_label)

# ==============================================================================================================================================================================

def add_expense(date, category, amount, description, transaction_date):
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, category, amount, description, transaction_date])

# ==============================================================================================================================================================================

def view_expenses():
    df = pd.read_csv(file_name)
    return df

# ==============================================================================================================================================================================

def update_table(tree, df, total_amount_label):
    for i in tree.get_children():
        tree.delete(i)
    
    total_amount = 0
    for index, row in df.iterrows():
        try:
            amount = float(row["Amount"])  # Convert the amount to float
        except ValueError:
            amount = 0  # If conversion fails, set amount to 0
        
        total_amount += amount
        
        # Apply alternating row colors (light grid effect)
        tag = 'evenrow' if index % 2 == 0 else 'oddrow'
        
        # Insert values into the Treeview
        tree.insert("", tk.END, values=(row["Date"], row["Category"], f"{currency_symbol}{amount:.2f}", row["Description"], row["Transaction Date"]), tags=(tag,))
    
    # Update total amount with the currency symbol
    total_amount_label.config(text=f"{translations[current_language]['total_amount']} {currency_symbol}{total_amount:.2f}")

# ==============================================================================================================================================================================

# Function to handle sorting by date
def sort_by_date(tree, total_amount_label):
    global sort_descending
    sort_descending = not sort_descending

    df = view_expenses()
    df = df.sort_values(by='Date', ascending=not sort_descending)

    update_table(tree, df, total_amount_label)

# ==============================================================================================================================================================================

# Function to handle adding an expense from the form inputs
def add_expense_from_form(tree, total_amount_label, date_entry, category_entry, amount_entry, description_entry, transaction_date_entry):
    date = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()
    description = description_entry.get()
    transaction_date = transaction_date_entry.get()

    if not date or not category or not amount or not description or not transaction_date:
        messagebox.showerror(translations[current_language]['error'], translations[current_language]['error_select'])
        return
    
    try:
        amount = float(amount)  # Ensure the amount is a number
    except ValueError:
        messagebox.showerror(translations[current_language]['error'], translations[current_language]['error_select'])
        return
    
    add_expense(date, category, amount, description, transaction_date)
    update_table(tree, view_expenses(), total_amount_label)
    
    # Clear the input fields
    date_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    transaction_date_entry.delete(0, tk.END)

# ==============================================================================================================================================================================

# Function to modify a selected expense directly in the input fields
def modify_expense(tree, date_entry, category_entry, amount_entry, description_entry, transaction_date_entry):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror(translations[current_language]['error'], translations[current_language]['error_select'])
        return

    # Get selected expense values and populate input fields
    item = tree.item(selected_item)
    expense_values = item['values']

    # Populate the input fields with the selected row's values
    date_entry.delete(0, tk.END)
    date_entry.insert(0, expense_values[0])
    
    category_entry.delete(0, tk.END)
    category_entry.insert(0, expense_values[1])
    
    amount_entry.delete(0, tk.END)
    amount_entry.insert(0, expense_values[2].replace(currency_symbol, ''))
    
    description_entry.delete(0, tk.END)
    description_entry.insert(0, expense_values[3])
    
    transaction_date_entry.delete(0, tk.END)
    transaction_date_entry.insert(0, expense_values[4])

# ==============================================================================================================================================================================

# Function to save the modified expense back to the CSV file
def save_modified_expense(tree, total_amount_label, date_entry, category_entry, amount_entry, description_entry, transaction_date_entry):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror(translations[current_language]['error'], translations[current_language]['error_select'])
        return

    # Get updated values from the input fields
    new_date = date_entry.get()
    new_category = category_entry.get()
    new_amount = amount_entry.get()
    new_description = description_entry.get()
    new_transaction_date = transaction_date_entry.get()

    if not new_date or not new_category or not new_amount or not new_description or not new_transaction_date:
        messagebox.showerror(translations[current_language]['error'], translations[current_language]['error_select'])
        return

    try:
        new_amount = float(new_amount)
    except ValueError:
        messagebox.showerror(translations[current_language]['error'], translations[current_language]['error_select'])
        return

    # Get selected expense values to identify the row in the CSV
    item = tree.item(selected_item)
    expense_values = item['values']

    # Delete the old record from the CSV
    df = pd.read_csv(file_name)
    df = df[(df['Date'] != expense_values[0]) |
            (df['Category'] != expense_values[1]) |
            (df['Amount'] != float(expense_values[2].replace(currency_symbol, '').strip())) |
            (df['Description'] != expense_values[3])]
    
    # Append the modified record
    df = df.append({'Date': new_date, 'Category': new_category, 'Amount': new_amount, 'Description': new_description, 'Transaction Date': new_transaction_date}, ignore_index=True)
    df.to_csv(file_name, index=False)

    # Update the table and reset input fields
    update_table(tree, df, total_amount_label)
    date_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    transaction_date_entry.delete(0, tk.END)

# ==============================================================================================================================================================================

def delete_selected_expense(tree, total_amount_label):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror(translations[current_language]['error'], translations[current_language]['error_select'])
        return

    # Get the selected expense
    item = tree.item(selected_item)
    expense_values = item['values']

    # Read the CSV data
    df = pd.read_csv(file_name)

    # Create a mask to find the matching row
    mask = (
        (df['Date'] == expense_values[0]) &
        (df['Category'] == expense_values[1]) &
        (df['Amount'].astype(str) == expense_values[2].replace(currency_symbol, '').strip()) &
        (df['Description'] == expense_values[3])
    )

    # Drop the matching row
    df = df[~mask]

    # Save the updated data to the CSV
    df.to_csv(file_name, index=False)

    # Update the table
    update_table(tree, df, total_amount_label)

    messagebox.showinfo("Success", "Expense deleted successfully.")

# ==============================================================================================================================================================================

# Function to switch language
def switch_language(lang, window, labels, entries, buttons, total_amount_label, tree):
    global current_language
    current_language = lang

    # Update window title and labels with selected language
    window.title(translations[current_language]['title'])
    for label_key, label in labels.items():
        label.config(text=translations[current_language][label_key])

    # Update buttons text
    for button_key, button in buttons.items():
        button.config(text=translations[current_language][button_key])

    # Update column headers based on selected language
    tree.heading("Date", text=translations[current_language]['date'])
    tree.heading("Category", text=translations[current_language]['category'])
    tree.heading("Amount", text=translations[current_language]['amount'])
    tree.heading("Description", text=translations[current_language]['description'])
    tree.heading("Transaction Date", text=translations[current_language]['transaction_date'])

    # Update total amount label text
    amount_str = total_amount_label.cget('text').replace(currency_symbol, '').strip().split()[-1]
    total_amount_label.config(text=f"{translations[current_language]['total_amount']} {currency_symbol}{float(amount_str):.2f}")

# ==============================================================================================================================================================================

# Function to display the expenses in a new window with form inputs, delete, search, modify, and total amount functionality
def display_expenses_window():
    expenses_df = view_expenses()
    
    # Create a new window
    window = tk.Tk()
    window.title(translations[current_language]['title'])

    # Set the window to be resizable and full screen based on platform
    window.geometry("1920x1080")  # Set an initial size (width x height)
    window.resizable(True, True)  # Allow resizing
    
    # Create a Treeview widget to display the data in tabular form
    tree = ttk.Treeview(window)
    
    # Define the columns
    tree['columns'] = ('Date', 'Category', 'Amount', 'Description', 'Transaction Date')

    # Format columns
    tree.column("#0", width=0, stretch=tk.NO)  # Hidden column
    tree.column("Date", anchor=tk.CENTER, width=100)
    tree.column("Category", anchor=tk.CENTER, width=100)
    tree.column("Amount", anchor=tk.CENTER, width=100)
    tree.column("Description", anchor=tk.CENTER, width=200)
    tree.column("Transaction Date", anchor=tk.CENTER, width=150)

    # Create column headers
    tree.heading("Date", text=translations[current_language]['date'], anchor=tk.CENTER, command=lambda: sort_by_date(tree, total_amount_label))
    tree.heading("Category", text=translations[current_language]['category'], anchor=tk.CENTER)
    tree.heading("Amount", text=translations[current_language]['amount'], anchor=tk.CENTER)
    tree.heading("Description", text=translations[current_language]['description'], anchor=tk.CENTER)
    tree.heading("Transaction Date", text=translations[current_language]['transaction_date'], anchor=tk.CENTER)

    # Add striped row effect by creating tags
    tree.tag_configure('evenrow', background='lightgray')
    tree.tag_configure('oddrow', background='white')

    tree.pack(pady=20, fill=tk.BOTH, expand=True)

    # Create a label to display the total amount
    total_amount_label = tk.Label(window, text=f"{translations[current_language]['total_amount']} {currency_symbol}0.00")
    total_amount_label.pack(pady=10)

    # Create input fields for adding a new expense
    form_frame = tk.Frame(window)
    form_frame.pack(pady=10)

    # Create labels and input fields
    labels = {
        'date': tk.Label(form_frame, text=translations[current_language]['date']),
        'category': tk.Label(form_frame, text=translations[current_language]['category']),
        'amount': tk.Label(form_frame, text=translations[current_language]['amount']),
        'description': tk.Label(form_frame, text=translations[current_language]['description']),
        'transaction_date': tk.Label(form_frame, text=translations[current_language]['transaction_date'])
    }

    # Grid the labels and input fields
    date_entry = tk.Entry(form_frame)
    category_entry = tk.Entry(form_frame)
    amount_entry = tk.Entry(form_frame)
    description_entry = tk.Entry(form_frame)
    transaction_date_entry = tk.Entry(form_frame)

    labels['date'].grid(row=0, column=0)
    date_entry.grid(row=0, column=1)

    labels['category'].grid(row=1, column=0)
    category_entry.grid(row=1, column=1)

    labels['amount'].grid(row=2, column=0)
    amount_entry.grid(row=2, column=1)

    labels['description'].grid(row=3, column=0)
    description_entry.grid(row=3, column=1)

    labels['transaction_date'].grid(row=4, column=0)
    transaction_date_entry.grid(row=4, column=1)

    # Create buttons and link them to their functions
    buttons = {
        'add_expense': tk.Button(window, text=translations[current_language]['add_expense'], 
                                 command=lambda: add_expense_from_form(tree, total_amount_label, date_entry, category_entry, amount_entry, description_entry, transaction_date_entry)),
        'delete_expense': tk.Button(window, text=translations[current_language]['delete_expense'], 
                                    command=lambda: delete_selected_expense(tree, total_amount_label)),
        'modify_expense': tk.Button(window, text=translations[current_language]['modify_expense'], 
                                    command=lambda: modify_expense(tree, date_entry, category_entry, amount_entry, description_entry, transaction_date_entry)),
        'save_expense': tk.Button(window, text=translations[current_language]['save_expense'], 
                                  command=lambda: save_modified_expense(tree, total_amount_label, date_entry, category_entry, amount_entry, description_entry, transaction_date_entry))
    }

    buttons['add_expense'].pack(pady=10)
    buttons['delete_expense'].pack(pady=10)
    buttons['modify_expense'].pack(pady=10)
    buttons['save_expense'].pack(pady=10)

    # Search bar frame
    search_frame = tk.Frame(window)
    search_frame.pack(pady=10)

    # Create a dropdown to select the column to search
    search_column = ttk.Combobox(search_frame, values=[
        translations[current_language]['date'],
        translations[current_language]['category'],
        translations[current_language]['amount'],
        translations[current_language]['description'],
        translations[current_language]['transaction_date']
    ], state="readonly")
    search_column.set(translations[current_language]['select_column'])
    search_column.pack(side=tk.LEFT, padx=10)

    # Create the search entry
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=10)

    # Create the search button
    search_button = tk.Button(search_frame, text=translations[current_language]['search'], 
                              command=lambda: search_expenses(tree, total_amount_label, search_entry, search_column))
    search_button.pack(side=tk.LEFT, padx=10)

    # Add a dropdown to select the language
    language_frame = tk.Frame(window)
    language_frame.pack(pady=20)
    tk.Label(language_frame, text=translations[current_language]['language']).pack(side=tk.LEFT, padx=10)

    language_selector = ttk.Combobox(language_frame, values=['English', 'Français'], state="readonly")
    language_selector.current(0 if current_language == 'en' else 1)
    language_selector.pack(side=tk.LEFT)

    # Function to change the language when selected from the dropdown
    def change_language(event):
        selected_language = 'en' if language_selector.get() == 'English' else 'fr'
        switch_language(selected_language, window, labels, [date_entry, category_entry, amount_entry, description_entry, transaction_date_entry], buttons, total_amount_label, tree)

    language_selector.bind("<<ComboboxSelected>>", change_language)

    # Display the data in the table and total amount
    update_table(tree, expenses_df, total_amount_label)

    # Start the Tkinter loop
    window.mainloop()

# Display expenses in a new window
display_expenses_window()
