
import os
import uuid
from flask import Flask, render_template, request, send_file, redirect, flash, url_for
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2docx import Converter

app = Flask(__name__)
app.secret_key = 'secret_key'
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge', methods=['GET', 'POST'])
def merge_pdfs():
    if request.method == 'POST':
        files = request.files.getlist('pdfs')
        if not files or files[0].filename == '':
            flash('Please upload PDF files.', 'error')
            return redirect(request.url)

        merger = PdfMerger()
        for f in files:
            merger.append(f)

        output_path = os.path.join(OUTPUT_FOLDER, f"merged_{uuid.uuid4().hex}.pdf")
        with open(output_path, 'wb') as f:
            merger.write(f)

        return send_file(output_path, as_attachment=True)

    return render_template('merge.html')

@app.route('/split', methods=['GET', 'POST'])
def split_pdf():
    if request.method == 'POST':
        file = request.files.get('pdf')
        if not file or file.filename == '':
            flash('Please upload a PDF file.', 'error')
            return redirect(request.url)

        reader = PdfReader(file)
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            output_path = os.path.join(OUTPUT_FOLDER, f"page_{i+1}_{uuid.uuid4().hex}.pdf")
            with open(output_path, 'wb') as f:
                writer.write(f)

        flash('PDF split into individual pages.', 'success')
        return redirect(url_for('index'))

    return render_template('split.html')

@app.route('/compress', methods=['GET', 'POST'])
def compress_pdf():
    if request.method == 'POST':
        file = request.files.get('pdf')
        if not file or file.filename == '':
            flash('Please upload a PDF file.', 'error')
            return redirect(request.url)

        reader = PdfReader(file)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        output_path = os.path.join(OUTPUT_FOLDER, f"compressed_{uuid.uuid4().hex}.pdf")
        with open(output_path, 'wb') as f:
            writer.write(f)

        return send_file(output_path, as_attachment=True)

    return render_template('compress.html')

@app.route('/convert', methods=['GET', 'POST'])
def convert_pdf():
    if request.method == 'POST':
        file = request.files.get('pdf')
        if not file or file.filename == '':
            flash('Please upload a PDF file.', 'error')
            return redirect(request.url)

        input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}.pdf")
        file.save(input_path)
        output_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4().hex}.docx")

        try:
            cv = Converter(input_path)
            cv.convert(output_path)
            cv.close()
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            flash('PDF to Word conversion failed.', 'error')
            return redirect(request.url)

    return render_template('convert.html')
