from flask import Flask, request, render_template, send_file, jsonify
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
import io


app = Flask(__name__)

DATABASE_PATH = '/tmp/reimbursements.db'
# Function to connect to the database
def connect_db():
    return sqlite3.connect(DATABASE_PATH)


# Function to generate a unique serial number starting with "DIGREIM"
def generate_serial_number():
    prefix = "DIGMA"
    conn = connect_db()
    cursor = conn.cursor()

    # Query to find the last serial number starting with "DIGMA"
    cursor.execute(
        "SELECT serial_number FROM reimbursements WHERE serial_number LIKE ? ORDER BY serial_number DESC LIMIT 1",
        (prefix + '%',)
    )

    last_serial = cursor.fetchone()  # Get the last serial number
    print("Last serial fetched from DB:", last_serial)  # Debugging: Check what's returned

    if last_serial:
        # Extract the numeric part of the serial number and increment it
        last_number = int(last_serial[0][len(prefix):])  # Strip "DIGMA" and convert to int
        next_number = last_number + 1  # Increment the last serial number
    else:
        # Start from 1 if no previous serial number is found
        next_number = 1

    # Format the new serial number (e.g., DIGMA0006)
    new_serial_number = f"{prefix}{next_number:04d}"
    print("Generated new serial number:", new_serial_number)  # Debugging: Check the new serial number

    # Commit the generated serial number to the database to make sure it's saved
    cursor.execute(
        "INSERT INTO reimbursements (serial_number) VALUES (?)",
        (new_serial_number,)
    )
    conn.commit()  # Ensure the new serial number is saved to the database

    conn.close()
    return new_serial_number


# Function to generate a PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import io
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import io
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics  # Import pdfmetrics to register the fonts
import os
import io

# Specify the base path and font paths
base_path = os.path.dirname(__file__)  # Get the current script's directory
bold_font_path = os.path.join(base_path, 'fonts', 'DejaVuSans-Bold.ttf')
regular_font_path = os.path.join(base_path, 'fonts', 'DejaVuSans.ttf')

# Register the fonts
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', "/Users/shabeer/Desktop/shabeer-app/fonts/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont('DejaVuSans', "/Users/shabeer/Desktop/shabeer-app/fonts/DejaVuSans.ttf"))

def create_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Set the font for the title and other important sections
    c.setFont("DejaVuSans-Bold", 18)
    c.drawString(100, 750, "Digma Bills")

    # Header information (use DejaVuSans-Bold for headers)
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(100, 720, f"Serial Number: {data['serial_number']}")
    c.drawString(100, 700, f"Employee ID: {data['employee_id']}")
    c.drawString(100, 680, f"Name: {data['name']}")

    # Line for separation
    c.line(100, 650, 500, 650)

    # Title for the table (bold font)
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(100, 630, "Reimbursement Details:")

    # Table for reimbursement details (Date column before Amount column)
    table_data = [["Date", "Description", "Brand", "Amount"]]  # Reordered columns with "Date" before "Amount"
    total_amount = 0
    for amount_data in data['amounts']:
        table_data.append([
            data['date'],  # Date field first
            amount_data['description'],
            amount_data['brand'],
            f"₹{amount_data['amount']:.2f}"  # Amount with ₹ symbol
        ])
        total_amount += amount_data['amount']  # Sum the amounts for the total

    # Define column widths
    col_widths = [1.5 * inch, 4 * inch, 2 * inch, 2 * inch]

    # Create and style the table
    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment for all cells
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),  # Header font (bold)
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),  # Apply 'DejaVuSans' font to all table cells (data rows)
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size for all cells
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Body background color
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines for the table
    ]))

    # Center the table by adjusting the X position
    table_width = sum(col_widths)
    x_position = (letter[0] - table_width) / 2  # Center horizontally on the page
    table.wrapOn(c, 0, 0)
    table.drawOn(c, x_position, 450)  # Adjust Y position to fit the table correctly

    # Display total amount below the table (bold font for emphasis)
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(100, 250, f"Total: ₹{total_amount:.2f}")  # Using Unicode for ₹

    # Footer with signature area
    c.setFont("DejaVuSans", 10)  # Use regular font for footer text
    c.drawString(100, 230, "Signature: ________________________")
    c.drawString(100, 210, "Date: _____________________________")

    # Generate the filename based on the serial number
    filename = f"{data['serial_number']}.pdf"

    # Save the PDF and return the buffer and filename
    c.save()
    buffer.seek(0)

    return buffer, filename
# Return both the buffer and filename
# Route for the HTML form
@app.route('/')
def form():
    return render_template('form.html')


# Route to handle form submission
# Route to handle form submission
@app.route('/submit', methods=['POST'])
@app.route('/submit', methods=['POST'])
@app.route('/submit', methods=['POST'])
@app.route('/submit', methods=['POST'])

def submit():
    # Generate the serial number with the "DIGMA" prefix
    serial_number = generate_serial_number()

    # Collecting data from the form
    data = {
        'serial_number': serial_number,  # Serial number with DIGMA prefix
        'employee_id': request.form['employee_id'],
        'name': request.form['name'],
        'date': request.form['date'],  # Get the date from the form
        'amounts': []
    }

    # Collecting the amounts, descriptions, and brands from the form
    for i in range(len(request.form.getlist('amount'))):
        amount = request.form.getlist('amount')[i]
        description = request.form.getlist('description')[i]
        brand = request.form.getlist('brand')[i] if 'brand' in request.form else 'N/A'

        data['amounts'].append({
            'amount': float(amount),
            'description': description,
            'brand': brand
        })

    # Pass the data to the PDF creation function
    pdf_buffer, filename = create_pdf(data)  # Unpack the tuple into pdf_buffer and filename

    # Return the PDF as a response
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
def setup_database():
    # Ensure the database and tables are set up correctly
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reimbursements (
                        id INTEGER PRIMARY KEY,
                        employee_id TEXT,
                        name TEXT,
                        date TEXT,
                        serial_number TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reimbursement_amounts (
                        id INTEGER PRIMARY KEY,
                        reimbursement_id INTEGER,
                        amount REAL,
                        description TEXT,
                        FOREIGN KEY (reimbursement_id) REFERENCES reimbursements (id))''')
    conn.commit()
    conn.close()

new_serial_number = generate_serial_number()
print("Generated serial number:", new_serial_number)
if __name__ == '__main__':
    setup_database()
    app.run(host='0.0.0.0', port=8080, debug=True)
