from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import os

app = Flask(__name__)

# Folder penyimpanan file yang sudah diolah
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

# Pastikan folder untuk upload dan hasil olahan ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def upload_file():
    return render_template('upload.html')  # HTML untuk upload file

@app.route('/upload', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file:
        # Simpan file yang di-upload
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        # Baca dan olah file Excel
        df = pd.read_excel(file_path)

        # Pilih kolom yang dibutuhkan
        kolom_dipilih = ['order_details_id', 'product_qty', 'product_price', 'product_order_date']
        df_filtered = df[kolom_dipilih]

        # Konversi kolom 'product_order_date' ke tipe datetime
        df_filtered['product_order_date'] = pd.to_datetime(df_filtered['product_order_date'], errors='coerce')
        df_filtered['product_order_date'] = df_filtered['product_order_date'].dt.date

        # Menambahkan kolom 'net' yang merupakan hasil perkalian 'product_price' dengan 'product_qty'
        df_filtered['net'] = df_filtered['product_price'] * df_filtered['product_qty']

        # Menambahkan kolom 'tax' yang merupakan 10% dari kolom 'net'
        df_filtered['tax'] = df_filtered['net'] * 0.10

        # Filter data yang bulan >= 10
        df_filtered = df_filtered[pd.to_datetime(df_filtered['product_order_date']).dt.month >= 11]

        # Simpan hasil ke file Excel baru
        output_filename = f'processed_{file.filename}'
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        df_filtered.to_excel(output_path, index=False)

        # Berikan file hasil olahan untuk diunduh
        return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

