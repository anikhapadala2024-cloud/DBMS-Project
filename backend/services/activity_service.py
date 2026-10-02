from backend.database import db
from backend.models.activity import CultivationActivity
from backend.models.batch import CropBatch
from backend.models.field import Field
from backend.utils.validators import parse_date

VALID_ACTIVITY_TYPES = ["Irrigation", "Fertilization", "Pest/Disease", "Harvesting"]

class ActivityService:
    @staticmethod
    def get_all(
        batch_id: int | None = None,
        activity_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        farmer_id: int | None = None
    ):
        query = CultivationActivity.query.outerjoin(CropBatch)

        if farmer_id is not None:
            query = query.outerjoin(Field, CropBatch.field_id == Field.field_id).filter(Field.farmer_id == farmer_id)

        if batch_id:
            query = query.filter(CultivationActivity.batch_id == batch_id)

        if activity_type and activity_type != "All":
            query = query.filter(CultivationActivity.activity_type == activity_type)

        d_from = parse_date(date_from)
        if d_from:
            query = query.filter(CultivationActivity.activity_date >= d_from)

        d_to = parse_date(date_to)
        if d_to:
            query = query.filter(CultivationActivity.activity_date <= d_to)

        activities = query.order_by(CultivationActivity.activity_date.desc(), CultivationActivity.activity_id.desc()).all()
        return [a.to_dict() for a in activities]

    @staticmethod
    def get_by_id(activity_id: int):
        activity = CultivationActivity.query.get(activity_id)
        if not activity:
            return None
        return activity.to_dict()

    @staticmethod
    def create(data: dict):
        batch_id = data.get("batch_id")
        activity_type = data.get("activity_type")
        activity_date_raw = data.get("activity_date")
        description = data.get("description")
        quantity_used = data.get("quantity_used")
        unit = data.get("unit")
        target_crop = (data.get("crop_name") or data.get("target_crop_name") or "").strip()

        if batch_id not in (None, ""):
            if not CropBatch.query.get(int(batch_id)):
                return None, "A valid Crop Batch must be selected."

        if not activity_type or activity_type not in VALID_ACTIVITY_TYPES:
            return None, f"Activity type must be one of: {', '.join(VALID_ACTIVITY_TYPES)}"

        activity_date = parse_date(activity_date_raw)
        if not activity_date:
            return None, "A valid activity date (YYYY-MM-DD) is required."

        if not description or not description.strip():
            return None, "Activity description is required."

        try:
            qty_val = float(quantity_used) if quantity_used is not None else 0.0
            if qty_val < 0:
                return None, "Quantity used cannot be negative."
        except (ValueError, TypeError):
            return None, "Quantity used must be a valid number."

        if not unit or not unit.strip():
            return None, "Unit (e.g., Liters, Kg, Hours) is required."

        activity = CultivationActivity()
        if batch_id not in (None, ""):
            activity.batch_id = int(batch_id)
        if target_crop:
            activity.crop_name = target_crop
        activity.activity_type = activity_type
        activity.activity_date = activity_date
        activity.description = description.strip()
        activity.quantity_used = qty_val
        activity.unit = unit.strip()
        db.session.add(activity)

        # If activity is Harvesting, also update the batch's yield or status if needed
        if activity_type == "Harvesting" and qty_val > 0 and activity.batch_id:
            batch = CropBatch.query.get(batch_id)
            if batch:
                batch.yield_amount = qty_val
                batch.actual_harvest_date = activity_date
                batch.status = "Harvested"

        db.session.commit()
        return activity.to_dict(), None

    @staticmethod
    def update(activity_id: int, data: dict):
        activity = CultivationActivity.query.get(activity_id)
        if not activity:
            return None, "Activity not found."

        if "activity_type" in data and data["activity_type"] in VALID_ACTIVITY_TYPES:
            activity.activity_type = data["activity_type"]

        if "activity_date" in data:
            ad = parse_date(data["activity_date"])
            if ad:
                activity.activity_date = ad

        if "description" in data and data["description"].strip():
            activity.description = data["description"].strip()

        if "quantity_used" in data and data["quantity_used"] is not None:
            try:
                activity.quantity_used = max(0.0, float(data["quantity_used"]))
            except (ValueError, TypeError):
                return None, "Quantity used must be a valid number."

        if "unit" in data and data["unit"].strip():
            activity.unit = data["unit"].strip()

        if "crop_name" in data and data["crop_name"] is not None:
            activity.crop_name = str(data["crop_name"]).strip() or None

        db.session.commit()
        return activity.to_dict(), None

    @staticmethod
    def delete(activity_id: int):
        activity = CultivationActivity.query.get(activity_id)
        if not activity:
            return False, "Activity not found."

        db.session.delete(activity)
        db.session.commit()
        return True, None
