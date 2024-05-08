from app import db

class UserAPI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.String(64), nullable=False)
    api_hash = db.Column(db.String(128), nullable=False)

