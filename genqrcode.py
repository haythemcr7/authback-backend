# genqrcode.py

import qrcode
import os

# ✅ URL de base vers ton frontend (localhost ou déploiement)
BASE_URL = "http://localhost:3000/table"

# 📁 Dossier de sortie des QR codes
OUTPUT_DIR = "public/qr"

# 🔢 Nombre de tables
NB_TABLES = 10

# 📂 Crée le dossier s'il n'existe pas
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 📸 Génère un QR code par table
for table_id in range(1, NB_TABLES + 1):
    url = f"{BASE_URL}/{table_id}"
    img = qrcode.make(url)
    img_path = os.path.join(OUTPUT_DIR, f"table_{table_id}.png")
    img.save(img_path)
    print(f"✅ QR généré : {img_path}")
