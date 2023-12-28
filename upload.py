from flask import Flask, request, send_from_directory
import pandas as pd

app = Flask(__name__, static_folder='static')

@app.route('/', methods=['GET'])
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/test', methods=['GET'])
def test_route():
    return 'Test route is working!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'greenbutton-data' not in request.files:
        return 'No file part'
    file = request.files['greenbutton-data']
    if file.filename == '':
        return 'No selected file'
    if file:
        df = pd.read_csv(file)
        # Now you can use the DataFrame `df` to analyze the data
        # ...
        return 'File successfully uploaded and read into DataFrame'

if __name__ == '__main__':
    app.run(debug=True)