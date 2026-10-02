from datetime import datetime
from backend.database import db

class Crop(db.Model):
    __tablename__ = "crops"

    crop_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    crop_name = db.Column(db.String(100), unique=True, nullable=False)
    crop_type = db.Column(db.String(50), nullable=False)
    season = db.Column(db.String(50), nullable=False)
    expected_yield = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    batches = db.relationship("CropBatch", back_populates="crop", cascade="all, delete-orphan", lazy="select")

    def to_dict(self):
        return {
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "crop_type": self.crop_type,
            "season": self.season,
            "expected_yield": float(self.expected_yield) if self.expected_yield is not None else 0.0,
            "batches_count": len(self.batches) if self.batches else 0,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
