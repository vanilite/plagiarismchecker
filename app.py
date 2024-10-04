from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from utils import extract_text_from_file, extract_random_phrases, search_google, scrape_content, compare_text
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORT_FOLDER'] = 'reports'
app.config['ALLOWED_EXTENSIONS'] = {'docx', 'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({'error': f'File save error: {str(e)}'}), 500

    try:
        # Process the file and get results
        text = extract_text_from_file(file_path)
        phrases = extract_random_phrases(text)

        matches = []
        for phrase in phrases:
            search_results = search_google(phrase)
            for result in search_results[:5]:
                scraped_content = scrape_content(result['url'])
                similarity = compare_text(text, scraped_content)
                if similarity > 0.5:  # Example threshold
                    matches.append({'phrase': phrase, 'url': result['url'], 'similarity': similarity})

        similarity_percentage = len(matches) / len(phrases) * 100

        # Generate PDF report
        report_filename = generate_pdf_report(filename, similarity_percentage, matches)
        report_path = os.path.join(app.config['REPORT_FOLDER'], report_filename)

        return send_file(report_path, as_attachment=True)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_pdf_report(filename, similarity_percentage, matches):
    report_filename = f"{os.path.splitext(filename)[0]}_report.pdf"
    report_path = os.path.join(app.config['REPORT_FOLDER'], report_filename)

    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 100, f"Plagiarism Report for {filename}")
    c.drawString(100, height - 120, f"Similarity: {similarity_percentage:.2f}%")

    y_position = height - 160
    for match in matches:
        c.drawString(100, y_position, f"Phrase: {match['phrase']}")
        c.drawString(100, y_position - 20, f"URL: {match['url']}")
        y_position -= 60
        if y_position < 100:
            c.showPage()
            y_position = height - 100

    c.save()
    return report_filename

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
    app.run(debug=True)