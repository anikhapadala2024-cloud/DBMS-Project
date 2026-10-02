from datetime import datetime
from backend.database import db

class Farmer(db.Model):
    __tablename__ = "farmers"

    farmer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    village = db.Column(db.String(100), nullable=False)
    land_size_acres = db.Column(db.Float, nullable=True)
    soil_type = db.Column(db.String(80), nullable=True)
    preferred_crop = db.Column(db.String(120), nullable=True)
    profile_photo_url = db.Column(db.String(500), nullable=True)
    farm_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="farmer_profile")
    fields = db.relationship("Field", back_populates="farmer", cascade="all, delete-orphan", lazy="select")

    def to_dict(self):
        return {
            "farmer_id": self.farmer_id,
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "village": self.village,
            "land_size_acres": float(self.land_size_acres) if self.land_size_acres is not None else None,
            "soil_type": self.soil_type,
            "preferred_crop": self.preferred_crop,
            "profile_photo_url": self.profile_photo_url,
            "farm_notes": self.farm_notes,
            "fields_count": len(self.fields) if self.fields else 0,
            "total_area": sum(float(f.area) for f in self.fields) if self.fields else 0.0,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
