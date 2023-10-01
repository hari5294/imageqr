import os
import base64
from flask import Flask, render_template, request, send_file
import qrcode
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'C:\\Users\\AHR\\Desktop\\qr creator\\uploads'  # Update with your upload directory
STATIC_FOLDER = 'static'  # Folder for static files like styles.css

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# Function to generate a QR code with customizable options
def generate_qr_code(data, size='medium', color='black', position='bottom', bg_color='#ffffff'):
    qr_box_size = 1  # Default box size
    if size == 'small':
        qr_box_size = 5  # Smaller box size
    elif size == 'medium':
        qr_box_size = 10  # Medium box size
    elif size == 'large':
        qr_box_size = 15  # Larger box size

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=qr_box_size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color=color, back_color=bg_color)

    return qr_image

# Function to overlay the QR code on the image
def overlay_qr_code_on_image(image_path, qr_image, position):
    image = Image.open(image_path)

    # Calculate the position to overlay the QR code based on the specified position
    if position == 'bottom':
        qr_position = (
            (image.width - qr_image.width) // 2,
            image.height - qr_image.height - 10
        )
    elif position == 'center':
        qr_position = (
            (image.width - qr_image.width) // 2,
            (image.height - qr_image.height) // 2
        )
    elif position == 'top':
        qr_position = (
            (image.width - qr_image.width) // 2,
            10
        )
    else:
        qr_position = (10, 10)  # Default to top-left

    image.paste(qr_image, qr_position)

    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return "No image part"
    
    image = request.files['image']
    
    if image.filename == '':
        return "No selected image"
    
    if image:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(filename)

    link = request.form.get('link')
    size = request.form.get('size', 'medium')
    color = request.form.get('color', 'black')
    position = request.form.get('position', 'bottom')
    bg_color = request.form.get('bg-color', '#ffffff')  # Get the background color

    qr_image = generate_qr_code(link, size, color, position, bg_color)  # Pass the background color to the generator

    if qr_image:
        image_with_qr = overlay_qr_code_on_image(filename, qr_image, position)
        output_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'output_image.png')
        image_with_qr.save(output_filename)

        with open(output_filename, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        return render_template('result.html', image_data=image_data)  # Render the result.html template
    else:
        return "Invalid QR code customization options."

@app.route('/download')
def download():
    output_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'output_image.png')
    return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    output_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'output_image.png')
    if os.path.exists(output_filename):
        os.remove(output_filename)
    
    app.run(debug=True)
