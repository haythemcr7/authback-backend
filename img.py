from rembg import remove
from PIL import Image
import os

# 📁 Chemin d'entrée et sortie
input_folder = "static/boissons"
output_folder = "static/boissons_clean"

# ✅ Crée le dossier de sortie s'il n'existe pas
os.makedirs(output_folder, exist_ok=True)

# 🔁 Traite chaque fichier image
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            input_path = os.path.join(root, file)

            # Recrée la structure du dossier
            relative_path = os.path.relpath(input_path, input_folder)
            output_path = os.path.join(output_folder, os.path.splitext(relative_path)[0] + ".png")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            print(f"🎨 Traitement : {relative_path}")

            with open(input_path, "rb") as i:
                result = remove(i.read())
                with open(output_path, "wb") as o:
                    o.write(result)

print("✅ Traitement terminé.")
