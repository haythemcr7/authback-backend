# run.py
from app import create_app
from pymongo import MongoClient

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
