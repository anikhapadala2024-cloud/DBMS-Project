from datetime import datetime
from backend.database import db

STATUS_LIFECYCLE_ORDER = {
    "Planned": 1,
    "Planted": 2,
    "Growing": 3,
    "Ready for Harvest": 4,
    "Harvested": 5
}

class CropBatch(db.Model):
    __tablename__ = "crop_batches"

    batch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    field_id = db.Column(db.Integer, db.ForeignKey("fields.field_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.crop_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    batch_code = db.Column(db.String(50), unique=True, nullable=False)
    planting_date = db.Column(db.Date, nullable=False)
    expected_harvest_date = db.Column(db.Date, nullable=False)
    actual_harvest_date = db.Column(db.Date, nullable=True)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    # Using 'yield' column in DB while mapping to yield_amount in Python model
    yield_amount = db.Column("yield", db.Numeric(10, 2), nullable=True, default=0.00)
    status = db.Column(db.String(30), nullable=False, default="Planned")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    field = db.relationship("Field", back_populates="batches")
    crop = db.relationship("Crop", back_populates="batches")
    activities = db.relationship("CultivationActivity", back_populates="batch", cascade="all, delete-orphan", order_by="desc(CultivationActivity.activity_date)")

    @property
    def lifecycle_stage(self) -> int:
        """Returns 1 to 5 representing current lifecycle progress."""
        return STATUS_LIFECYCLE_ORDER.get(self.status, 1)

    @property
    def lifecycle_percentage(self) -> int:
        stage = self.lifecycle_stage
        return int((stage / 5) * 100)

    def to_dict(self):
        farmer_obj = self.field.farmer if self.field else None
        return {
            "batch_id": self.batch_id,
            "batch_code": self.batch_code,
            "field_id": self.field_id,
            "field_name": self.field.field_name if self.field else "Unknown",
            "field_location": self.field.location if self.field else "",
            "field_area": float(self.field.area) if self.field and self.field.area else 0.0,
            "farmer_id": farmer_obj.farmer_id if farmer_obj else None,
            "farmer_name": farmer_obj.name if farmer_obj else "Unknown",
            "crop_id": self.crop_id,
            "crop_name": self.crop.crop_name if self.crop else "Unknown",
            "crop_type": self.crop.crop_type if self.crop else "Unknown",
            "planting_date": self.planting_date.strftime("%Y-%m-%d") if self.planting_date else None,
            "expected_harvest_date": self.expected_harvest_date.strftime("%Y-%m-%d") if self.expected_harvest_date else None,
            "actual_harvest_date": self.actual_harvest_date.strftime("%Y-%m-%d") if self.actual_harvest_date else None,
            "quantity": float(self.quantity) if self.quantity is not None else 0.0,
            "yield": float(self.yield_amount) if self.yield_amount is not None else 0.0,
            "status": self.status,
            "lifecycle_stage": self.lifecycle_stage,
            "lifecycle_percentage": self.lifecycle_percentage,
            "activities_count": len(self.activities) if self.activities else 0,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
