from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="farmer")  # 'admin' or 'farmer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    farmer_profile = db.relationship("Farmer", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, raw_password: str):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    def to_dict(self, include_farmer_id: bool = True):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
        if include_farmer_id and self.farmer_profile:
            data["farmer_id"] = self.farmer_profile.farmer_id
        else:
            data["farmer_id"] = None
        return data
