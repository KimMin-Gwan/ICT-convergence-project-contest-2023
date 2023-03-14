from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def upload_file():
    # 업로드된 파일 저장
    file = request.files['file']
    file.save(os.path.join('./upload', file.filename))
    return 'File uploaded successfully'

if __name__ == '__main__':
    context = ('cert.pem', 'key.pem')
    app.run(debug=True, ssl_context=context)