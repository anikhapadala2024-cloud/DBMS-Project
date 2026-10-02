from datetime import datetime, date
import random
import string
from backend.database import db
from backend.models.batch import CropBatch, STATUS_LIFECYCLE_ORDER
from backend.models.field import Field
from backend.models.crop import Crop
from backend.models.farmer import Farmer
from backend.utils.validators import parse_date
from sqlalchemy import or_

VALID_STATUSES = ["Planned", "Planted", "Growing", "Ready for Harvest", "Harvested"]

class BatchService:
    @staticmethod
    def generate_code(crop_id: int = None) -> str:
        """Generate a clean, readable unique batch code."""
        prefix = "BATCH"
        year = datetime.now().year
        crop_code = "CRP"
        farmer_tag = "F"
        if crop_id:
            crop = Crop.query.get(crop_id)
            if crop and crop.crop_name:
                cleaned = "".join([ch for ch in crop.crop_name if ch.isalnum()]).upper()
                crop_code = cleaned[:3] if len(cleaned) >= 3 else "CRP"

        candidate = f"{prefix}-{year}-{farmer_tag}-{crop_code}"
        if not CropBatch.query.filter_by(batch_code=candidate).first():
            return candidate

        # Ensure uniqueness
        for _ in range(20):
            suffix = "".join(random.choices(string.digits, k=3))
            candidate = f"{prefix}-{year}-{crop_code}{suffix}"
            if not CropBatch.query.filter_by(batch_code=candidate).first():
                return candidate

        random_chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{year}-{random_chars}"

    @staticmethod
    def get_all(
        crop_id: int = None,
        farmer_id: int = None,
        field_id: int = None,
        status: str = None,
        date_from: str = None,
        date_to: str = None,
        search: str = None
    ):
        query = CropBatch.query.join(Field).join(Crop).join(Farmer, Field.farmer_id == Farmer.farmer_id)

        if crop_id:
            query = query.filter(CropBatch.crop_id == crop_id)
        if field_id:
            query = query.filter(CropBatch.field_id == field_id)
        if farmer_id:
            query = query.filter(Field.farmer_id == farmer_id)
        if status and status != "All":
            query = query.filter(CropBatch.status == status)

        d_from = parse_date(date_from)
        if d_from:
            query = query.filter(CropBatch.planting_date >= d_from)

        d_to = parse_date(date_to)
        if d_to:
            query = query.filter(CropBatch.planting_date <= d_to)

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    CropBatch.batch_code.ilike(term),
                    Crop.crop_name.ilike(term),
                    Field.field_name.ilike(term),
                    Farmer.name.ilike(term)
                )
            )

        batches = query.order_by(CropBatch.batch_id.desc()).all()
        return [b.to_dict() for b in batches]

    @staticmethod
    def get_by_id(batch_id: int):
        batch = CropBatch.query.get(batch_id)
        if not batch:
            return None
        data = batch.to_dict()
        data["activities"] = [a.to_dict() for a in batch.activities]
        return data

    @staticmethod
    def create(data: dict):
        field_id = data.get("field_id")
        crop_id = data.get("crop_id")
        planting_date_raw = data.get("planting_date")
        expected_harvest_raw = data.get("expected_harvest_date")
        quantity = data.get("quantity")
        status = data.get("status", "Planned")
        batch_code = data.get("batch_code")

        if not field_id or not Field.query.get(field_id):
            return None, "A valid Field must be selected."
        if not crop_id or not Crop.query.get(crop_id):
            return None, "A valid Crop must be selected."

        planting_date = parse_date(planting_date_raw)
        if not planting_date:
            return None, "Valid planting date (YYYY-MM-DD) is required."

        expected_harvest_date = parse_date(expected_harvest_raw)
        if not expected_harvest_date:
            return None, "Valid expected harvest date (YYYY-MM-DD) is required."

        if expected_harvest_date < planting_date:
            return None, "Expected harvest date cannot be prior to planting date."

        try:
            qty_val = float(quantity)
            if qty_val <= 0:
                return None, "Quantity must be greater than 0."
        except (ValueError, TypeError):
            return None, "Quantity must be a valid positive number."

        if status not in VALID_STATUSES:
            status = "Planned"

        # Auto-generate or validate batch_code
        if not batch_code or not batch_code.strip():
            batch_code = BatchService.generate_code(int(crop_id))
        else:
            batch_code = batch_code.strip().upper()
            if CropBatch.query.filter_by(batch_code=batch_code).first():
                return None, f"Batch code '{batch_code}' is already registered."

        actual_harvest_date = parse_date(data.get("actual_harvest_date"))
        yield_val = 0.0
        if "yield" in data and data["yield"] is not None:
            try:
                yield_val = max(0.0, float(data["yield"]))
            except (ValueError, TypeError):
                yield_val = 0.0

        batch = CropBatch(
            field_id=int(field_id),
            crop_id=int(crop_id),
            batch_code=batch_code,
            planting_date=planting_date,
            expected_harvest_date=expected_harvest_date,
            actual_harvest_date=actual_harvest_date,
            quantity=qty_val,
            yield_amount=yield_val,
            status=status
        )
        db.session.add(batch)
        db.session.commit()
        return batch.to_dict(), None

    @staticmethod
    def update(batch_id: int, data: dict):
        batch = CropBatch.query.get(batch_id)
        if not batch:
            return None, "Crop batch not found."

        if "field_id" in data and data["field_id"]:
            if not Field.query.get(data["field_id"]):
                return None, "Specified field does not exist."
            batch.field_id = int(data["field_id"])

        if "crop_id" in data and data["crop_id"]:
            if not Crop.query.get(data["crop_id"]):
                return None, "Specified crop does not exist."
            batch.crop_id = int(data["crop_id"])

        if "planting_date" in data:
            pd = parse_date(data["planting_date"])
            if pd:
                batch.planting_date = pd

        if "expected_harvest_date" in data:
            ehd = parse_date(data["expected_harvest_date"])
            if ehd:
                batch.expected_harvest_date = ehd

        if batch.expected_harvest_date < batch.planting_date:
            return None, "Expected harvest date cannot be prior to planting date."

        if "actual_harvest_date" in data:
            batch.actual_harvest_date = parse_date(data["actual_harvest_date"])

        if "quantity" in data and data["quantity"] is not None:
            try:
                qty_val = float(data["quantity"])
                if qty_val > 0:
                    batch.quantity = qty_val
            except (ValueError, TypeError):
                return None, "Quantity must be a valid number."

        if "yield" in data and data["yield"] is not None:
            try:
                batch.yield_amount = max(0.0, float(data["yield"]))
            except (ValueError, TypeError):
                return None, "Yield must be a valid number."

        if "status" in data and data["status"] in VALID_STATUSES:
            batch.status = data["status"]
            if batch.status == "Harvested" and not batch.actual_harvest_date:
                batch.actual_harvest_date = date.today()

        db.session.commit()
        return batch.to_dict(), None

    @staticmethod
    def update_status(batch_id: int, new_status: str, yield_amount: float = None, actual_harvest_date_str: str = None):
        batch = CropBatch.query.get(batch_id)
        if not batch:
            return None, "Crop batch not found."

        if new_status not in VALID_STATUSES:
            return None, f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"

        batch.status = new_status
        if new_status == "Harvested":
            if actual_harvest_date_str:
                batch.actual_harvest_date = parse_date(actual_harvest_date_str) or date.today()
            elif not batch.actual_harvest_date:
                batch.actual_harvest_date = date.today()

            if yield_amount is not None:
                try:
                    batch.yield_amount = max(0.0, float(yield_amount))
                except (ValueError, TypeError):
                    pass

        db.session.commit()
        return batch.to_dict(), None

    @staticmethod
    def delete(batch_id: int):
        batch = CropBatch.query.get(batch_id)
        if not batch:
            return False, "Crop batch not found."

        db.session.delete(batch)
        db.session.commit()
        return True, None
