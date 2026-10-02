from backend.database import db
from backend.models.crop import Crop
from sqlalchemy import or_

class CropService:
    @staticmethod
    def get_all(search: str = None):
        query = Crop.query

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Crop.crop_name.ilike(term),
                    Crop.crop_type.ilike(term),
                    Crop.season.ilike(term)
                )
            )

        crops = query.order_by(Crop.crop_name.asc()).all()
        return [c.to_dict() for c in crops]

    @staticmethod
    def get_by_id(crop_id: int):
        crop = Crop.query.get(crop_id)
        if not crop:
            return None
        data = crop.to_dict()
        data["batches"] = [b.to_dict() for b in crop.batches]
        return data

    @staticmethod
    def create(data: dict):
        crop_name = data.get("crop_name")
        crop_type = data.get("crop_type")
        season = data.get("season")
        expected_yield = data.get("expected_yield")

        if not crop_name or not crop_name.strip():
            return None, "Crop name is required."
        if not crop_type or not crop_type.strip():
            return None, "Crop type is required."
        if not season or not season.strip():
            return None, "Season is required."
        try:
            yield_val = float(expected_yield)
            if yield_val <= 0:
                return None, "Expected yield must be greater than 0."
        except (ValueError, TypeError):
            return None, "Expected yield must be a valid number."

        # Check unique
        if Crop.query.filter(Crop.crop_name.ilike(crop_name.strip())).first():
            return None, f"Crop '{crop_name.strip()}' already exists."

        crop = Crop(
            crop_name=crop_name.strip(),
            crop_type=crop_type.strip(),
            season=season.strip(),
            expected_yield=yield_val
        )
        db.session.add(crop)
        db.session.commit()
        return crop.to_dict(), None

    @staticmethod
    def update(crop_id: int, data: dict):
        crop = Crop.query.get(crop_id)
        if not crop:
            return None, "Crop not found."

        if "crop_name" in data and data["crop_name"].strip():
            new_name = data["crop_name"].strip()
            existing = Crop.query.filter(Crop.crop_name.ilike(new_name), Crop.crop_id != crop_id).first()
            if existing:
                return None, f"Crop name '{new_name}' is already used by another crop."
            crop.crop_name = new_name

        if "crop_type" in data and data["crop_type"].strip():
            crop.crop_type = data["crop_type"].strip()
        if "season" in data and data["season"].strip():
            crop.season = data["season"].strip()
        if "expected_yield" in data and data["expected_yield"] is not None:
            try:
                yield_val = float(data["expected_yield"])
                if yield_val > 0:
                    crop.expected_yield = yield_val
            except (ValueError, TypeError):
                return None, "Expected yield must be a valid number."

        db.session.commit()
        return crop.to_dict(), None

    @staticmethod
    def delete(crop_id: int):
        crop = Crop.query.get(crop_id)
        if not crop:
            return False, "Crop not found."

        if crop.batches:
            return False, f"Cannot delete crop '{crop.crop_name}' because it has {len(crop.batches)} associated crop batch(es)."

        db.session.delete(crop)
        db.session.commit()
        return True, None
