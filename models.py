#회원가입
from sqlalchemy import Column, Integer, VARCHAR, DateTime
from datetime import datetime
from pymongo import MongoClient #mongodb 연동
from flask_login import UserMixin

client = MongoClient("mongodb://localhost:27017/")
db = client["register"]


#회원 테이블
class User(db.Model, UserMixin):
    user_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(120), nullable=False)
    hashed_pw = db.Column(db.String(200))


