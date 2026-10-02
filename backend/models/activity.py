from datetime import datetime
from backend.database import db

class CultivationActivity(db.Model):
    __tablename__ = "cultivation_activities"

    activity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("crop_batches.batch_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    crop_name = db.Column(db.String(120), nullable=True)
    activity_type = db.Column(db.String(30), nullable=False)  # 'Irrigation', 'Fertilization', 'Pest/Disease', 'Harvesting'
    activity_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity_used = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    unit = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    batch = db.relationship("CropBatch", back_populates="activities")

    def to_dict(self):
        batch_obj = self.batch
        field_obj = batch_obj.field if batch_obj else None
        farmer_obj = field_obj.farmer if field_obj else None
        crop_obj = batch_obj.crop if batch_obj else None

        return {
            "activity_id": self.activity_id,
            "batch_id": self.batch_id,
            "batch_code": batch_obj.batch_code if batch_obj else "Manual Entry",
            "crop_name": self.crop_name or (crop_obj.crop_name if crop_obj else "Unknown"),
            "farmer_name": farmer_obj.name if farmer_obj else "Unknown",
            "activity_type": self.activity_type,
            "activity_date": self.activity_date.strftime("%Y-%m-%d") if self.activity_date else None,
            "description": self.description,
            "quantity_used": float(self.quantity_used) if self.quantity_used is not None else 0.0,
            "unit": self.unit,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
