#실행 : flask run

#회원가입 > 로그인 > 로그인 이후 화면(pdf 파일 업로드 화면)

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from pymongo import MongoClient
import jwt
import hashlib 
import datetime

app = Flask(__name__)

client = MongoClient('mongodb://localhost', 27017) #mongodb 회원정보 저장
db = client.dbsparta_plus_week4

SECRET_KEY = 'ITT'

@app.route('/login') #로그인
def login():
    msg = request.args.get("msg")
    return render_template ('login.html', msg=msg)


@app.route('/register') #회원가입
def register():
    return render_template('register.html')


@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    db.user.insert_one({'id':id_receive, 'pw':pw_hash})

    return jsonify({'result':'success'})


@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form('id_give')
    pw_receive = request.form('pw_give')

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8').hexdigest())

    result = db.user.find_one({'id': id_receive, 'pw':pw_hash})


    if result is not None:
        payload = {
            'id' : id_receive,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result':'success', 'token':token})
    else:
        return jsonify({'result': 'fail', 'msg': 'ID/PW 불일치'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

