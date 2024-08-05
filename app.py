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
import hashlib

# Load configuration from config.toml file
with open('j:\\data science\\VS code\\arihant agro\\config.toml', 'r') as file:
    config = pytoml.load(file)

# Access database credentials
DB_HOST = config['Arihant_agro']['host']
DB_USER = config['Arihant_agro']['user']
DB_PASSWORD = config['Arihant_agro']['password']
DB_NAME = config['Arihant_agro']['name']

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

@st.cache(allow_output_mutation=True)
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

# Function to generate PDF statement
def get_statement(customer_name, start_date, end_date):
    
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
    sale_query = f"SELECT s.sale_date AS 'Date', s.GST AS Particulars, s.challan_number AS 'Vch.no', s.total_price AS Debit, NULL AS credit FROM sale s WHERE s.customer_name = '{customer_name}'"
    purchase_query = f"SELECT p.purchase_date AS 'Date', p.GST as Particulars, p.invoice_number AS 'Vch.no', NULL AS Debit, p.total_price as credit FROM purchase p WHERE p.customer_name = '{customer_name}'"
    payment_query = f"SELECT pay.payment_date AS 'Date', pay.payment_method as Particulars, pay.invoice_number AS 'Vch.no', NULL AS Debit, pay.amount as credit FROM payment pay WHERE pay.customer_name = '{customer_name}'"
    
    sale_data = fetch_data_from_mysql(sale_query)
    purchase_data = fetch_data_from_mysql(purchase_query)
    payment_data = fetch_data_from_mysql(payment_query)

    # Combine all data
    combined_data = sale_data + purchase_data + payment_data
    combined_data = sorted(combined_data, key=lambda x: x[0])  # Sort by date

    # Add table headers
    data = [['Date', 'Particulars', 'Vch.no', 'Debit', 'Credit']] + combined_data
    table = Table(data, colWidths=[1.5 * inch] * 5)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    # Calculate column widths based on content
    col_widths = [max([len(str(row[i])) for row in data]) for i in range(5)]
    for i, width in enumerate(col_widths):
        col_widths[i] = max(width * 0.1 * inch, 1.5 * inch)  # Adjust this factor as needed

    # Update table column widths
    table._argW = col_widths

    table.wrapOn(c, 500, 600)
    table.drawOn(c, 72, 600 - len(data) * 20)

    # Add a summary
    c.drawCentredString(400, 620 - len(data) * 20, "Thank you for your business!")

    c.showPage()
    c.save()

    # Convert PDF to Base64 for download link
    with open(f"{customer_name}.pdf", "rb") as pdf_file:
        pdf_base64 = base64.b64encode(pdf_file.read()).decode("utf-8")

    return pdf_base64

# Main Streamlit app
def main():
    st.title("Arihant Agro Management System")

    menu = ["Customer", "Inventory", "Purchase", "Sale", "Payment", "Generate Statement"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Customer":
        st.subheader("Customer Management")
        st.write("Add new customer")
        customer_name = st.text_input("Customer Name")
        contact = st.text_input("Contact")
        address = st.text_input("Address")

        if st.button("Add Customer"):
            create_customer(customer_name, contact, address)
            st.success(f"Customer '{customer_name}' added successfully")

        st.write("Delete customer")
        customer_id = st.text_input("Customer ID")
        if st.button("Delete Customer"):
            delete_customer(customer_id)
            st.success(f"Customer with ID '{customer_id}' deleted successfully")

        st.write("View customers")
        df = display_customers()
        st.dataframe(df)

    elif choice == "Inventory":
        st.subheader("Inventory Management")
        st.write("Add new product")
        product_name = st.text_input("Product Name")
        quantity = st.number_input("Quantity", min_value=0)
        price = st.number_input("Price", min_value=0.0)
        unit = st.text_input("Unit")

        if st.button("Add Product"):
            create_product(product_name, quantity, price, unit)
            st.success(f"Product '{product_name}' added successfully")

        st.write("Delete product")
        product_id = st.text_input("Product ID")
        if st.button("Delete Product"):
            delete_product(product_id)
            st.success(f"Product with ID '{product_id}' deleted successfully")

        st.write("View inventory")
        df = display_inventory()
        st.dataframe(df)

    elif choice == "Purchase":
        st.subheader("Purchase Management")
        st.write("Add new purchase")
        purchase_date = st.date_input("Purchase Date")
        invoice_number = st.text_input("Invoice Number")
        product = st.text_input("Product")
        quantity = st.number_input("Quantity", min_value=0)
        customer_name = st.text_input("Customer Name")
        total_price = st.number_input("Total Price", min_value=0.0)
        gst = st.text_input("GST")

        if st.button("Add Purchase"):
            create_purchase(purchase_date, invoice_number, product, quantity, customer_name, total_price, gst)
            st.success(f"Purchase for '{product}' added successfully")

        st.write("Delete purchase")
        purchase_id = st.text_input("Purchase ID")
        if st.button("Delete Purchase"):
            delete_purchase(purchase_id)
            st.success(f"Purchase with ID '{purchase_id}' deleted successfully")

        st.write("View purchases")
        df = display_purchases()
        st.dataframe(df)

    elif choice == "Sale":
        st.subheader("Sale Management")
        st.write("Add new sale")
        sale_date = st.date_input("Sale Date")
        total_price = st.number_input("Total Price", min_value=0.0)
        product_name = st.text_input("Product Name")
        customer_name = st.text_input("Customer Name")
        challan_number = st.text_input("Challan Number")
        quantity = st.number_input("Quantity", min_value=0)
        gst = st.text_input("GST")

        if st.button("Add Sale"):
            create_sale(sale_date, total_price, product_name, customer_name, challan_number, quantity, gst)
            st.success(f"Sale for '{product_name}' added successfully")

        st.write("Delete sale")
        sale_id = st.text_input("Sale ID")
        if st.button("Delete Sale"):
            delete_sale(sale_id)
            st.success(f"Sale with ID '{sale_id}' deleted successfully")

        st.write("View sales")
        df = display_sales()
        st.dataframe(df)

    elif choice == "Payment":
        st.subheader("Payment Management")
        st.write("Add new payment")
        invoice_number = st.text_input("Invoice Number")
        payment_date = st.date_input("Payment Date")
        amount = st.number_input("Amount", min_value=0.0)
        payment_method = st.text_input("Payment Method")
        note = st.text_input("Note")
        customer_name = st.text_input("Customer Name")
        payment_direction = st.selectbox("Payment Direction", ["Debit", "Credit"])

        if st.button("Add Payment"):
            create_payment(invoice_number, payment_date, amount, payment_method, note, customer_name, payment_direction)
            st.success(f"Payment for invoice '{invoice_number}' added successfully")

        st.write("Delete payment")
        payment_id = st.text_input("Payment ID")
        if st.button("Delete Payment"):
            delete_payment(payment_id)
            st.success(f"Payment with ID '{payment_id}' deleted successfully")

        st.write("View payments")
        df = display_payment()
        st.dataframe(df)

    elif choice == "Generate Statement":
        st.subheader("Generate Customer Statement")
        customer_name = st.text_input("Customer Name")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

        if st.button("Generate Statement"):
            pdf_base64 = get_statement(customer_name, start_date, end_date)
            href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="{customer_name}_statement.pdf">Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
