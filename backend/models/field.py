from datetime import datetime
from backend.database import db

class Field(db.Model):
    __tablename__ = "fields"

    field_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey("farmers.farmer_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    area = db.Column(db.Numeric(8, 2), nullable=False)  # Acres
    soil_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    farmer = db.relationship("Farmer", back_populates="fields")
    batches = db.relationship("CropBatch", back_populates="field", cascade="all, delete-orphan", lazy="select")

    def to_dict(self):
        return {
            "field_id": self.field_id,
            "farmer_id": self.farmer_id,
            "farmer_name": self.farmer.name if self.farmer else "Unassigned",
            "field_name": self.field_name,
            "location": self.location,
            "area": float(self.area) if self.area is not None else 0.0,
            "soil_type": self.soil_type,
            "batches_count": len(self.batches) if self.batches else 0,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
