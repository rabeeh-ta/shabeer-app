from flask import Flask, request, render_template, send_file
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import io

app = Flask(__name__)

DATABASE_PATH = '/tmp/reimbursements.db'

# Function to connect to the database
def connect_db():
    return sqlite3.connect(DATABASE_PATH)

# Function to set up the database and tables
def setup_database():
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
                        brand TEXT,
                        FOREIGN KEY (reimbursement_id) REFERENCES reimbursements (id))''')
    conn.commit()
    conn.close()

# Function to generate a unique serial number starting with "DIGMA"
def generate_serial_number():
    prefix = "DIGMA"
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT serial_number FROM reimbursements WHERE serial_number LIKE ? ORDER BY serial_number DESC LIMIT 1", (prefix + '%',))
    last_serial = cursor.fetchone()

    if last_serial:
        last_number = int(last_serial[0][len(prefix):])
        next_number = last_number + 1
    else:
        next_number = 1

    new_serial_number = f"{prefix}{next_number:04d}"
    cursor.execute("INSERT INTO reimbursements (serial_number) VALUES (?)", (new_serial_number,))
    conn.commit()
    conn.close()
    return new_serial_number

# Register fonts for PDF generation
base_path = os.path.dirname(__file__)
bold_font_path = os.path.join(base_path, 'fonts', 'DejaVuSans-Bold.ttf')
regular_font_path = os.path.join(base_path, 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font_path))
pdfmetrics.registerFont(TTFont('DejaVuSans', regular_font_path))

# Function to create a PDF
def create_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("DejaVuSans-Bold", 18)
    c.drawString(100, 750, "Digma Bills")

    # Header information
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(100, 720, f"Serial Number: {data['serial_number']}")
    c.drawString(100, 700, f"Employee ID: {data['employee_id']}")
    c.drawString(100, 680, f"Name: {data['name']}")

    c.line(100, 650, 500, 650)

    # Table for reimbursement details
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    # Calculate total width of the table and set position for centering with margin
    table_width = sum(col_widths)
    page_width = letter[0]
    margin = 0.5 * inch  # Space on each side (you can adjust this)

    # Ensure the table with margins doesn't exceed the page width
    if table_width + 2 * margin > page_width:
        margin = (page_width - table_width) / 2  # Adjust margin if needed

    # Calculate x_position for centering the table
    x_position = (page_width - table_width) / 2

    # Draw the table centered with margins
    table.wrapOn(c, 0, 0)
    table.drawOn(c, x_position, 450)

    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(100, 250, f"Total: ₹{total_amount:.2f}")

    c.setFont("DejaVuSans", 10)
    c.drawString(100, 230, "Signature: ________________________")
    c.drawString(100, 210, "Date: _____________________________")

    filename = f"{data['serial_number']}.pdf"
    c.save()
    buffer.seek(0)

    return buffer, filename

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    serial_number = generate_serial_number()

    data = {
        'serial_number': serial_number,
        'employee_id': request.form['employee_id'],
        'name': request.form['name'],
        'date': request.form['date'],
        'amounts': []
    }

    for i in range(len(request.form.getlist('amount'))):
        amount = request.form.getlist('amount')[i]
        description = request.form.getlist('description')[i]
        brand = request.form.getlist('brand')[i] if 'brand' in request.form else 'N/A'
        data['amounts'].append({
            'amount': float(amount),
            'description': description,
            'brand': brand
        })

    pdf_buffer, filename = create_pdf(data)
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

if __name__ == '__main__':
    setup_database()  # Ensure the database is set up correctly on startup
    app.run(host='0.0.0.0', port=8080, debug=True)
