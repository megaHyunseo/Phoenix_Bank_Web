from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
from config import Config
from models import db, User
from ocr import extract_text_from_image
import os

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

db.init_app(app)

# 전역 변수로 초음파 센서 데이터를 저장
sensor_data = {
    'distance': None
}

@app.route('/')
def index():
    return render_template('index.html', distance=sensor_data['distance'])

@app.route('/data', methods=['POST'])
def receive_data():
    global sensor_data
    data = request.get_json()
    sensor_data['distance'] = data['distance']
    socketio.emit('sensor_update', {'distance': sensor_data['distance']})

    if sensor_data['distance'] <= 10:
        return jsonify({'redirect': url_for('upload_page')}), 200

    return jsonify({'status': 'success'}), 200

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/extract_and_save', methods=['POST'])
def extract_and_save():
    file = request.files['file']
    save_path = '/home/piai/바탕화면/Phoenix_Bank_Web/uploaded_files'
    
    # 저장할 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    filename = os.path.join(save_path, file.filename)
    file.save(filename)
    
    try:
        name, registration_number = extract_text_from_image(filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    new_user = User(name=name, registration_number=registration_number)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    return render_template('upload.html', name=name, registration_number=registration_number)

@app.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'name': user.name, 'registration_number': user.registration_number} for user in users])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False)
