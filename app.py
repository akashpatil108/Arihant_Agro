from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
import streamlit as st
import base64
import os
import fitz
import subprocess
import mysql.connector
from datetime import datetime
import pandas as pd
import pytoml

# Access secrets directly through st.secrets
DB_HOST = st.secrets["Arihant_agro"]["host"]
DB_USER = st.secrets["Arihant_agro"]["user"]
DB_PASSWORD = st.secrets["Arihant_agro"]["password"]
DB_NAME = st.secrets["Arihant_agro"]["name"]

# Connect to MySQL database
connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = connection.cursor()

# Function to fetch data from MySQL
def fetch_data_from_mysql(query):
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

def fetch_customer_address(customer_name):
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
    cursor.execute(f"SELECT address FROM customers WHERE customer_name = '{customer_name}'")
    address = cursor.fetchone()[0]  # Assuming 'address' is the name of the column storing the address
    cursor.close()
    connection.close()
    return address

# Function to create a new customer entry
def create_customer(customer_name, contact, address):
    query = "INSERT INTO customers (customer_name, contact, address) VALUES (%s, %s, %s)"
    data = (customer_name, contact, address)
    cursor.execute(query, data)
    connection.commit()

# Function to delete a customer entry
def delete_customer(customer_id):
    # Convert customer_id to Python integer type
    customer_id = int(customer_id)
    query = "DELETE FROM customers WHERE customer_id = %s"
    data = (customer_id,)
    cursor.execute(query, data)
    connection.commit()

# Function to display all customers
def display_customers():
    query = "SELECT * FROM customers"
    cursor.execute(query)
    customers = cursor.fetchall()
    
    # Get column names
    columns = [col[0] for col in cursor.description]
    
    # Create DataFrame
    df = pd.DataFrame(customers, columns=columns)
    return df

# Function to create a new product entry
def create_product(product_name, quantity, price, unit):
    query = "INSERT INTO inventory (product_name, quantity, price, unit) VALUES (%s, %s, %s, %s)"
    data = (product_name, quantity, price, unit)
    cursor.execute(query, data)
    connection.commit()

# Function to delete a product entry
def delete_product(product_id):
    product_id=int(product_id)
    query = "DELETE FROM inventory WHERE product_id = %s"
    data = (product_id,)
    cursor.execute(query, data)
    connection.commit()

# Function to display all products in inventory
def display_inventory():
    query = "SELECT * FROM inventory"
    cursor.execute(query)
    inventory = cursor.fetchall()
    
    # Get column names
    columns = [col[0] for col in cursor.description]
    
    # Create DataFrame
    df = pd.DataFrame(inventory, columns=columns)
    return df

# Function to create a new purchase entry
def create_purchase(purchase_date, invoice_number, product, quantity, customer_name, total_price,gst):
    query = "INSERT INTO purchase (purchase_date, invoice_number, product, quantity, customer_name, total_price,gst) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (purchase_date, invoice_number, product, quantity, customer_name, total_price,gst)
    cursor.execute(query, data)
    connection.commit()

# Function to delete a purchase entry
def delete_purchase(purchase_id):
    purchase_id=int(purchase_id)
    query = "DELETE FROM purchase WHERE purchase_id = %s"
    data = (purchase_id,)
    cursor.execute(query, data)
    connection.commit()

# Function to display all purchases
def display_purchases():
    query = "SELECT * FROM purchase"
    cursor.execute(query)
    purchase = cursor.fetchall()
    # Get column names
    columns = [col[0] for col in cursor.description]
    # Create DataFrame
    df = pd.DataFrame(purchase, columns=columns)
    return df

# Function to create a new sale entry
def create_sale(sale_date, total_price, product_name, customer_name, challan_number, quantity, gst):
    query = "INSERT INTO sale (sale_date, total_price, product_name, customer_name, challan_number, quantity, gst) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (sale_date, total_price, product_name, customer_name, challan_number, quantity, gst)
    cursor.execute(query, data)
    connection.commit()

# Function to delete a sale entry
def delete_sale(sale_id):
    query = "DELETE FROM sale WHERE sale_id = %s"
    data = (sale_id,)
    cursor.execute(query, data)
    connection.commit()

# Function to display all sales
def display_sales():
    query = "SELECT * FROM sale"
    cursor.execute(query)
    sales = cursor.fetchall()
    
    # Get column names
    columns = [col[0] for col in cursor.description]
    
    # Create DataFrame
    df = pd.DataFrame(sales, columns=columns)
    return df

# Function to create a new payment entry
def create_payment(invoice_number, payment_date, amount, payment_method, note, customer_name, payment_direction):
    query = "INSERT INTO payment (invoice_number, payment_date, amount, payment_method, note, customer_name, payment_direction) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (invoice_number, payment_date, amount, payment_method, note, customer_name, payment_direction)
    cursor.execute(query, data)
    connection.commit()

# Function to delete a payment entry
def delete_payment(payment_id):
    payment_id=int(payment_id)
    query = "DELETE FROM payment WHERE payment_id = %s"
    data = (payment_id,)
    cursor.execute(query, data)
    connection.commit()

# Function to display all payments
def display_payment():
    query = "SELECT * FROM payment"
    cursor.execute(query)
    payment = cursor.fetchall()
    
    # Get column names
    columns = [col[0] for col in cursor.description]
    
    # Create DataFrame
    df = pd.DataFrame(payment, columns=columns)
    return df


def get_statement(customer_name, start_date, end_date):
    
    # path = f'j:\\data science\\VS code\\arihant agro\\{customer_name}.pdf'
    # c = canvas.Canvas(path, pagesize=letter)
    # Create a temporary directory if it doesn't exist
    customer_address = fetch_customer_address(customer_name)
    c = canvas.Canvas(f"{customer_name}.pdf", pagesize=letter)
    # Add header
    header_text = "Arihant Agro Industries"
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, header_text)

    # Add a statement
    statement = "At Shirgaon(K) Tal-Tasgaon Dist-Sangli"
    c.setFont("Helvetica", 12)
    c.drawCentredString(300, 730, statement)

    # Add customer name
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(300, 700, customer_name)
    customer_address= f"{customer_address}"
    # Add customer address
    c.setFont("Helvetica", 12)
    c.drawCentredString(300, 680, customer_address)

    # Add start date
    c.drawCentredString(300, 660, f"{start_date} to {end_date}")

    # Fetch data from MySQL
    sale_query = f"SELECT s.sale_date AS 'Date',        s.GST AS Particulars,   s.challan_number AS 'Vch.no', s.total_price AS Debit, NULL AS credit FROM sale s WHERE s.customer_name = '{customer_name}'"
    purchase_query = f"SELECT p.purchase_date AS 'Date',p.GST as Particulars,   p.invoice_number AS 'Vch.no', NULL AS Debit,   p.total_price as credit FROM purchase p WHERE p.customer_name = '{customer_name}'"
    payment_query = f"SELECT pay.payment_date AS 'Date',pay.payment_method as Particulars,  pay.invoice_number AS 'Vch.no', NULL AS Debit,  pay.amount as credit FROM payment pay WHERE pay.customer_name = '{customer_name}'"
    
    sale_data = fetch_data_from_mysql(sale_query)
    purchase_data = fetch_data_from_mysql(purchase_query)
    payment_data = fetch_data_from_mysql(payment_query)

    # Combine all data
    data = [("Date", "Particulars", "Vch.no", "Debit", "Credit")]  # Header row

    # Add sale data
    for row in sale_data:
        data.append(row)

    # Add purchase data
    for row in purchase_data:
        data.append(row)

    # Add payment data
    for row in payment_data:
        data.append(row)

    # Calculate width of the page
    width, height = letter
    table_width = width - 2 * inch  # 1 inch margin on both sides
    # Calculate total debit and credit
    debit_sum = sum(float(row[3]) if row[3] else 0 for row in data[1:])
    credit_sum = sum(float(row[4]) if row[4] else 0 for row in data[1:])

    # Append total rows
    data.append(("Total", "", "", debit_sum, credit_sum))
    

    # Create table
    table = Table(data, colWidths=[table_width / len(data[0])] * len(data[0]))
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.white), 
                                   ('BACKGROUND', (0, -1), (-1,-1), colors.lightblue),
                                   ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')]))  


    # Get table width
    table.wrapOn(c, width, height)

    # Position table - Adjusted vertical position to avoid overlap
    table.drawOn(c, inch, 500)
    # Save the canvas to the PDF file
    c.showPage()
    c.save()
    # Open the PDF in a new window using the default PDF viewer
    subprocess.Popen([f"{customer_name}.pdf"], shell=True)

# Main title and sidebar navigation
st.title("Arihant Agro Management System")

menu = ["Customer Management", "Inventory Management", "Purchase Management", "Sale Management", "Payment Management"]
choice = st.sidebar.selectbox("Navigation", menu)

# Customer Management Section
if choice == "Customer Management":
    st.header("Customer Management")

    # Add Customer Section
    st.subheader("Add New Customer")
    customer_name = st.text_input("Customer Name")
    contact = st.text_input("Contact")
    address = st.text_area("Address")
    if st.button("Add Customer"):
        create_customer(customer_name, contact, address)
        st.success("Customer added successfully.")

    # Delete Customer Section
    st.subheader("Delete Customer")
    customers = display_customers()
    selected_customer = st.selectbox("Select Customer", customers['customer_name'])
    if st.button("Delete Customer"):
        customer_id = customers[customers['customer_name'] == selected_customer]['customer_id'].iloc[0]
        delete_customer(customer_id)
        st.success("Customer deleted successfully.")

    # Display all Customers
    st.subheader("All Customers")
    all_customers = display_customers()
    st.table(all_customers)

# Inventory Management Section
elif choice == "Inventory Management":
    st.header("Inventory Management")

    # Add Product Section
    st.subheader("Add New Product")
    product_name = st.text_input("Product Name")
    quantity = st.number_input("Quantity", min_value=0)
    price = st.number_input("Price", min_value=0.0)
    unit = st.text_input("Unit")
    if st.button("Add Product"):
        create_product(product_name, quantity, price, unit)
        st.success("Product added to inventory successfully.")

    # Delete Product Section
    st.subheader("Delete Product")
    inventory = display_inventory()
    selected_product = st.selectbox("Select Product", inventory['product_name'])

    if st.button("Delete Product"):
        product_id = inventory[inventory['product_name'] == selected_product]['product_id'].iloc[0]
        delete_product(product_id)
        st.success("Product deleted from inventory successfully.")

    # Display all Products
    st.subheader("Current Inventory")
    all_products = display_inventory()
    st.table(all_products)

# Purchase Management Section
elif choice == "Purchase Management":
    st.header("Purchase Management")
    # Add Purchase Section
    st.subheader("Add New Purchase")
    customers = display_customers()
    inventory=display_inventory()
    purchase_date = st.date_input("Purchase Date")
    invoice_number = st.text_input("Invoice Number")
    product = st.selectbox("Select Product", inventory['product_name'])
    quantity = st.text_input("Quantity")
    customer_name = st.selectbox("Select Customer", customers['customer_name'])
    total_price = st.number_input("Total Price", min_value=0.0)
    gst = st.selectbox("GST", ["With GST", "Without GST"])    
    if st.button("Add Purchase"):
        create_purchase(purchase_date, invoice_number, product, quantity, customer_name, total_price,gst)
        st.success("Purchase added successfully.")

    # Delete Purchase Section
    st.subheader("Delete Purchase")
    purchases = display_purchases()
    selected_purchase = st.selectbox("Select Purchase", purchases['invoice_number'])
    if st.button("Delete Purchase"):
        purchase_id = purchases[purchases['invoice_number'] == selected_purchase]['purchase_id'].iloc[0]
        st.write(f'purchase id {purchase_id}')
        delete_purchase(purchase_id)
        st.success("Purchase deleted successfully.")

    # Display all Purchases
    st.subheader("All Purchases")
    all_purchases = display_purchases()
    st.table(all_purchases)

# Sale Management Section
elif choice == "Sale Management":
    st.header("Sale Management")

    # Add Sale Section
    st.subheader("Add New Sale")
    customers = display_customers()
    inventory=display_inventory()
    sale_date = st.date_input("Sale Date")
    total_price = st.number_input("Total Price", min_value=0.0)
    product_name =  st.selectbox("Select Product", inventory['product_name'])
    customer_name = st.selectbox("Select Customer", customers['customer_name'])
    challan_number = st.text_input("Challan Number")
    quantity = st.text_input("Quantity")
    gst = st.selectbox("GST", ["With GST", "Without GST"])
    if st.button("Add Sale"):
        create_sale(sale_date, total_price, product_name, customer_name, challan_number, quantity, gst)
        st.success("Sale added successfully.")

    # Delete Sale Section
    st.subheader("Delete Sale")
    sales = display_sales()
    selected_sale = st.selectbox("Select Sale", sales['sale_id'])
    if st.button("Delete Sale"):
        sale_id = sales[sales['sale_id'] == selected_sale]['sale_id'].iloc[0]
        delete_sale(sale_id)
        st.success("Sale deleted successfully.")

    # Display all Sales
    st.subheader("All Sales")
    all_sales = display_sales()
    st.table(all_sales)

# Payment Management Section
elif choice == "Payment Management":
    st.header("Payment Management")

    # Add Payment Section
    st.subheader("Add New Payment")
    customers = display_customers()
    invoice_number = st.text_input("Invoice Number")
    payment_date = st.date_input("Payment Date")
    amount = st.number_input("Amount", min_value=0.0)
    payment_method = st.text_input("Payment Method")
    note = st.text_area("Note")
    customer_name = st.selectbox("Select Customer", customers['customer_name'])
    payment_direction = st.selectbox("Payment Direction", ["Debited", "Credited"])
    if st.button("Add Payment"):
        create_payment(invoice_number, payment_date, amount, payment_method, note, customer_name, payment_direction)
        st.success("Payment added successfully.")

    # Delete Payment Section
    st.subheader("Delete Payment")
    payment = display_payment()
    selected_payment_id = st.selectbox("Select Payment to Delete", payment['payment_id'])
    if st.button("Delete Payment"):
        payment_id = payment[payment['payment_id'] == selected_payment_id]['payment_id'].iloc[0]
        delete_payment(payment_id)
        st.success("Payment deleted successfully.")

    # Display all Payment
    st.subheader("All Payment")
    all_payment = display_payment()
    st.table(all_payment)

st.sidebar.subheader("Get Statement")
customers = display_customers()
customer_name = st.sidebar.selectbox("Select the customer name", customers['customer_name'])
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

if st.sidebar.button("Get Statement"):
    get_statement(customer_name, start_date, end_date)
