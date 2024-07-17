from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///keys.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)  # CORS desteği ekleniyor

class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False)
    hwid = db.Column(db.String(50), nullable=True)
    usage_limit = db.Column(db.Integer, default=1)
    expiration_date = db.Column(db.DateTime)
    uses = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Key oluşturma endpointi
@app.route('/create_key', methods=['POST'])
def create_key():
    data = request.json
    key = data.get('key')
    usage_limit = data.get('usage_limit', 1)
    expiration_minutes = data.get('expiration_minutes', 60)
    expiration_date = datetime.now() + timedelta(minutes=expiration_minutes)
    
    new_key = Key(key=key, usage_limit=usage_limit, expiration_date=expiration_date)
    db.session.add(new_key)
    db.session.commit()
    
    return jsonify({"message": "Key created successfully"}), 201

# Geri kalan endpointler ve işlemler buraya ekleniyor...

@app.route('/keys', methods=['GET'])
def get_keys():
    keys = Key.query.all()
    keys_list = [
        {
            "id": key.id,
            "key": key.key,
            "hwid": key.hwid,
            "usage_limit": key.usage_limit,
            "expiration_date": key.expiration_date,
            "uses": key.uses,
        }
        for key in keys
    ]
    return jsonify(keys_list), 200

def delete_expired_keys():
    with app.app_context():
        while True:
            now = datetime.now()
            expired_keys = Key.query.filter(Key.expiration_date < now).all()
            for key in expired_keys:
                db.session.delete(key)
            db.session.commit()
            time.sleep(1)  # Her 1 saniyede bir kontrol et

# delete_expired_keys fonksiyonunu başlatma
if __name__ == '__main__':
    threading.Thread(target=delete_expired_keys, daemon=True).start()
    app.run(debug=True)
