from flask import Blueprint, jsonify, request
from app.models import get_users, create_user, get_user_by_login, get_user_by_phone
from flask_jwt_extended import create_access_token 
import bcrypt
from datetime import timedelta
from app.config import MongoConfig
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, get_jwt
from bson.objectid import ObjectId
from twilio.rest import Client
import os
from dotenv import load_dotenv








twilio_bp = Blueprint("twilio", __name__)
catalogue_bp = Blueprint('catalogue', __name__)
tables_bp = Blueprint("tables", __name__)
mongo_config = MongoConfig()


load_dotenv()






























@tables_bp.route("/tables", methods=["GET"])
def get_tables():
    try:
        tables_collection = mongo_config.get_collection("tables")
        tables = list(tables_collection.find())
        for t in tables:
            t["_id"] = str(t["_id"])  # rendre JSON serializable
        return jsonify(tables), 200
    except Exception as e:
        print("Erreur récupération des tables :", e)
        return jsonify({"error": "Erreur serveur"}), 500













@catalogue_bp.route('/catalogue-boissons', methods=['GET'])
def get_catalogue_boissons():
    try:
        boissons_collection = mongo_config.get_collection('boissons')
        boissons = list(boissons_collection.find())

        # Convertir les ObjectId pour qu'ils soient JSON sérialisables
        for b in boissons:
            b['_id'] = str(b['_id'])

        return jsonify(boissons), 200
    except Exception as e:
        print(f"Erreur catalogue : {e}")
        return jsonify({"error": "Erreur lors de la récupération du catalogue"}), 500
    
    
    
    
  
@catalogue_bp.route('/commande-boissons', methods=['POST'])
@jwt_required()
def passer_commande():
    if not request.is_json:
        print("❌ Requête non JSON")
        return jsonify({"error": "Le corps de la requête doit être au format JSON"}), 400

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corps de requête vide"}), 400

        # ✅ Récupérer le login (identity) et les claims personnalisés
        user_login = get_jwt_identity()  # "sallab"
        claims = get_jwt()
        user_id = claims.get("id")
        print(user_login);
        print(user_id);

        if not user_id or not user_login:
            return jsonify({"error": "Utilisateur non identifié"}), 401

        boissons = data.get('boissons')
        image_url = data.get('image_url', '')
        table = data.get('table_numero')
        print(table);

        if not boissons:
            return jsonify({"error": "Aucune boisson sélectionnée"}), 400

        commandes_collection = mongo_config.get_collection("commandes_boissons")

        commande = {
            "table":table,
            "user_id": user_id,
            "username": user_login,
            "boissons": boissons,
            "image_url": image_url,
            "statut": "en attente",
            "date_commande": datetime.utcnow()
        }

        commandes_collection.insert_one(commande)

        return jsonify({"message": "Commande enregistrée avec succès"}), 201

    except Exception as e:
        print("Erreur commande:", e)
        return jsonify({"error": "Erreur serveur"}), 500
    
    
    
    
    
    
    
    
    
    




admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/commandes', methods=['GET'])
def get_all_commandes():
    try:
        commandes = mongo_config.get_collection('commandes_boissons')
        docs = list(commandes.find())

        for c in docs:
            c["_id"] = str(c["_id"])

        return jsonify(docs), 200
    except Exception as e:
        print("Erreur récupération commandes admin:", e)
        return jsonify({"error": "Erreur serveur"}), 500


@admin_bp.route('/admin/commandes/<commande_id>/livrer', methods=['PATCH'])
@jwt_required()
def livrer_commande(commande_id):
    try:
        commandes_collection = mongo_config.get_collection('commandes_boissons')
        result = commandes_collection.update_one(
            {"_id": ObjectId(commande_id)},
            {"$set": {"statut": "livrée"}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Commande non trouvée"}), 404

        return jsonify({"message": "✅ Commande marquée comme livrée"}), 200

    except Exception as e:
        print("Erreur mise à jour commande:", e)
        return jsonify({"error": "Erreur serveur"}), 500



@admin_bp.route("/admin/archiver-commandes", methods=["POST"])
@jwt_required()
def archiver_commandes():
    if get_jwt_identity() != "admin":
        return jsonify({"error": "Accès refusé"}), 403

    commandes_boissons_col = mongo_config.get_collection("commandes_boissons")
    commandes_hist_col = mongo_config.get_collection("commandes_hist")

    commandes = list(commandes_boissons_col.find())

    if commandes:
        commandes_hist_col.insert_many(commandes)
        commandes_boissons_col.delete_many({})

    return jsonify({"message": "Commandes archivées avec succès."}), 200

















auth_bp = Blueprint('auth', __name__)
register_bp = Blueprint('register', __name__)

@auth_bp.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = get_users()
        return jsonify({
            "success": True,
            "count": len(users),
            "data": users
        })
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch users"
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('login') or not data.get('password'):
            return jsonify({"error": "Login and password are required"}), 400

        user = get_user_by_login(data['login'])
        print(user)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Récupération du hash stocké et vérification du mot de passe
        stored_hashed_pw = user['password_hash'].encode('utf-8')  # ⬅️ Convertir en bytes pour checkpw
        entered_pw = data['password'].encode('utf-8')

        if not bcrypt.checkpw(entered_pw, stored_hashed_pw):
            return jsonify({"error": "Invalid credentials"}), 401

        # Création du token JWT
        access_token = create_access_token(
    identity=user['login'],  # 👈 subject = string obligatoire
    additional_claims={"id":str(user["_id"])},
    expires_delta=timedelta(hours=2)
)


        return jsonify({
            "access_token": access_token,
            "user": {
                "id": str(user["_id"]),
                "login": user["login"]
            }
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500


@register_bp.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        
        login = data.get('login')
        password = data.get('password')
        phone_number = data.get('phone_number')

        if not login or not password or not phone_number:
            return jsonify({"error": "Login, password and phone number are required"}), 400

        # Vérifier si l'utilisateur existe déjà
        if get_user_by_login(login):
            return jsonify({"error": "Nom d'utilisateur déjà utilisé"}), 409

        # Vérifier si le numéro de téléphone est déjà utilisé
        if get_user_by_phone(phone_number):
            return jsonify({"error": "Numéro de téléphone déjà utilisé"}), 409

        # Créer l'utilisateur (la fonction create_user doit prendre aussi le phone_number)
        create_user(login, password, phone_number)
        user = get_user_by_login(login)

        access_token = create_access_token(
            identity=user['login'],
            additional_claims={"id": str(user["_id"])},
            expires_delta=timedelta(hours=2)
        )
        
        return jsonify({
            "success": True,
            "message": "Utilisateur inscrit avec succès",
            "access_token": access_token,
            "user": {
                "id": str(user["_id"]),
                "login": user["login"]
            }
        }), 201

    except Exception as e:
        print(f"Erreur d'inscription : {str(e)}")
        return jsonify({"error": "Échec de l'inscription"}), 500
    
    
    

@catalogue_bp.route('/commande-boissons/anonyme', methods=['POST'])
def passer_commande_anonyme():
    if not request.is_json:
        return jsonify({"error": "Le corps de la requête doit être JSON"}), 400

    try:
        data = request.get_json()
        user_id = data.get("user_id")
        username = data.get("username")
        table = data.get("table_numero")
        boissons = data.get("boissons")
        image_url = data.get("image_url", "")

        if not user_id or not table or not boissons:
            return jsonify({"error": "Champs requis manquants"}), 400

        commandes_collection = mongo_config.get_collection("commandes_boissons")

        commande = {
            "user_id": user_id,
            "username":username,
            "table_numero": table,
            "boissons": boissons,
            "image_url": image_url,
            "statut": "en attente",
            "date_commande": datetime.utcnow()
        }

        commandes_collection.insert_one(commande)

        return jsonify({"message": "✅ Commande anonyme enregistrée"}), 201

    except Exception as e:
        print("Erreur commande anonyme:", e)
        return jsonify({"error": "Erreur serveur"}), 500    