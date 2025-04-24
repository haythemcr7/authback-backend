# app/models.py

from app.config import MongoConfig
import bcrypt
from bson.objectid import ObjectId

mongo_config = MongoConfig()
users_collection = mongo_config.get_collection("users")

def get_users():
    users = list(users_collection.find())
    for u in users:
        u["_id"] = str(u["_id"])
    return users

def get_user_by_login(login):
    return users_collection.find_one({"login": login})

def get_user_by_phone(phone_number):
    return users_collection.find_one({"phone_number": phone_number})

def create_user(login, password, phone_number):
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = {
        "login": login,
        "password_hash": hashed_pw.decode("utf-8"),
        "phone_number": phone_number
    }
    users_collection.insert_one(user)
    return user
