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


def create_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Set up the title with styling
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 750, "Digma Bills")

    # Header information
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Serial Number: {data['serial_number']}")
    c.drawString(100, 700, f"Employee ID: {data['employee_id']}")
    c.drawString(100, 680, f"Name: {data['name']}")

    # Line for separation
    c.line(100, 650, 500, 650)

    # Title for the table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 630, "Reimbursement Details:")

    # Table for reimbursement details
    table_data = [["Date", "Amount", "Description", "Brand"]]  # Move Date to the first column
    total_amount = 0
    for amount_data in data['amounts']:
        table_data.append([
            data['date'],  # Date field now before Amount
            f"${amount_data['amount']:.2f}",
            amount_data['description'],
            amount_data['brand']
        ])
        total_amount += amount_data['amount']  # Sum the amounts for the total

    # Define column widths (adjusted for the new column order)
    col_widths = [2 * inch, 1.5 * inch, 4 * inch, 2 * inch]  # Adjust width for Date column

    # Create and style the table
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment for all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size for all cells
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Body background color
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines for the table
    ]))

    # Calculate table width and position to center it
    table_width = sum(col_widths)
    page_width = letter[0]  # 612 points (default letter size width)
    x_position = (page_width - table_width) / 2  # Calculate the x-position to center the table

    # Draw the table on the canvas
    table.wrapOn(c, 0, 0)
    table.drawOn(c, x_position, 450)  # Position the table in the center

    # Display total amount below the table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 250, f"Total: ${total_amount:.2f}")  # Adjust Y position for the total field

    # Footer with signature area
    c.setFont("Helvetica", 10)
    c.drawString(100, 230, "Signature: ________________________")
    c.drawString(100, 210, "Date: _____________________________")

    # Generate the filename based on the serial number
    filename = f"{data['serial_number']}.pdf"

    # Save the PDF and return the buffer and filename
    c.save()
    buffer.seek(0)

    return buffer, filename  # Return both the buffer and filename


# Return both the buffer and filename

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