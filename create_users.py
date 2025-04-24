from pymongo import MongoClient
import bcrypt
from app.config import MongoConfig


mongo_config = MongoConfig()
users_collection = mongo_config.get_collection("users")

# Utilisateurs de test
users_collection.insert_many([
    {
        "login": "admin",
        "password_hash": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
        "phone_number": "+212611111111"
    },
    {
        "login": "client1",
        "password_hash": bcrypt.hashpw("client123".encode(), bcrypt.gensalt()).decode(),
        "phone_number": "+212622222222"
    }
])

print("✅ Utilisateurs insérés dans MongoDB.")
