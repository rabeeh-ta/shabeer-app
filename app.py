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
    # Query to find the last serial number that starts with "DIGREIM"
    cursor.execute(
        "SELECT serial_number FROM reimbursements WHERE serial_number LIKE ? ORDER BY serial_number DESC LIMIT 1",
        (prefix + '%',))
    last_serial = cursor.fetchone()

    if last_serial:
        # Extract the numeric part and increment it
        last_number = int(last_serial[0][len(prefix):])  # Strip prefix and convert to int
        next_number = last_number + 1
    else:
        next_number = 1  # Start from 1 if no previous serial number is found

    # Format the new serial number
    new_serial_number = f"{prefix}{next_number:04d}"  # Pads the number with zeros to 4 digits
    conn.close()
    return new_serial_number


# Function to generate a PDF
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
    c.drawString(100, 660, f"Date: {data['date']}")

    # Line for separation
    c.line(100, 650, 500, 650)

    # Title for the table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 630, "Reimbursement Details:")

    # Table for reimbursement details
    table_data = [["Amount", "Description"]]  # Table header
    for amount_data in data['amounts']:
        table_data.append([f"${amount_data['amount']:.2f}", amount_data['description']])

    # Create and style the table
    table = Table(table_data, colWidths=[1.5 * inch, 4 * inch])
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

    # Draw the table on the canvas
    table.wrapOn(c, 0, 0)
    table.drawOn(c, 100, 500)  # Adjust Y position as needed

    # Footer with signature area
    c.setFont("Helvetica", 10)
    c.drawString(100, 450, "Signature: ________________________")
    c.drawString(100, 430, "Date: _____________________________")

    # Save the PDF and return the buffer
    c.save()
    buffer.seek(0)
    return buffer


# Route for the HTML form
@app.route('/')
def form():
    return render_template('form.html')


# Route to handle form submission
# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve form data
    employee_id = request.form['employee_id']
    name = request.form['name']
    date = request.form['date']
    descriptions = request.form.getlist('description')
    amounts = request.form.getlist('amount')

    # Convert amounts to floats
    amounts = [float(amt) for amt in amounts]

    # Generate a serial number
    serial_number = generate_serial_number()

    # Save to reimbursements table
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reimbursements (employee_id, name, date, serial_number) VALUES (?, ?, ?, ?)",
        (employee_id, name, date, serial_number)
    )
    reimbursement_id = cursor.lastrowid

    # Save each amount and description to the reimbursement_amounts table
    for desc, amt in zip(descriptions, amounts):
        cursor.execute(
            "INSERT INTO reimbursement_amounts (reimbursement_id, amount, description) VALUES (?, ?, ?)",
            (reimbursement_id, amt, desc)  # amt is already a float
        )

    conn.commit()
    conn.close()

    # Prepare data for PDF
    pdf_data = {
        'employee_id': employee_id,
        'name': name,
        'date': date,
        'serial_number': serial_number,
        'amounts': [{'amount': amt, 'description': desc} for amt, desc in zip(amounts, descriptions)]
    }
    pdf_buffer = create_pdf(pdf_data)

    # Return the PDF as a downloadable file
    return send_file(pdf_buffer, as_attachment=True, download_name=f"reimbursement_{serial_number}.pdf",
                     mimetype='application/pdf')


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


if __name__ == '__main__':
    setup_database()
    app.run(host='0.0.0.0', port=8080, debug=True)