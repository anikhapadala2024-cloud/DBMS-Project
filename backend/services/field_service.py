from backend.database import db
from backend.models.field import Field
from backend.models.farmer import Farmer
from sqlalchemy import or_

class FieldService:
    @staticmethod
    def get_all(farmer_id: int = None, search: str = None):
        query = Field.query

        if farmer_id:
            query = query.filter_by(farmer_id=farmer_id)

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.join(Farmer).filter(
                or_(
                    Field.field_name.ilike(term),
                    Field.location.ilike(term),
                    Field.soil_type.ilike(term),
                    Farmer.name.ilike(term)
                )
            )

        fields = query.order_by(Field.field_id.desc()).all()
        return [f.to_dict() for f in fields]

    @staticmethod
    def get_by_id(field_id: int):
        field = Field.query.get(field_id)
        if not field:
            return None
        data = field.to_dict()
        data["batches"] = [b.to_dict() for b in field.batches]
        return data

    @staticmethod
    def create(data: dict):
        farmer_id = data.get("farmer_id")
        field_name = data.get("field_name")
        location = data.get("location")
        area = data.get("area")
        soil_type = data.get("soil_type")

        if not farmer_id:
            return None, "A valid Farmer must be selected."
        if not Farmer.query.get(farmer_id):
            return None, f"Farmer with ID {farmer_id} does not exist."
        if not field_name or not field_name.strip():
            return None, "Field name is required."
        if not location or not location.strip():
            return None, "Field location is required."
        try:
            area_val = float(area)
            if area_val <= 0:
                return None, "Field area must be greater than 0."
        except (ValueError, TypeError):
            return None, "Field area must be a valid number."
        if not soil_type or not soil_type.strip():
            return None, "Soil type is required."

        field = Field(
            farmer_id=int(farmer_id),
            field_name=field_name.strip(),
            location=location.strip(),
            area=area_val,
            soil_type=soil_type.strip()
        )
        db.session.add(field)
        db.session.commit()
        return field.to_dict(), None

    @staticmethod
    def update(field_id: int, data: dict):
        field = Field.query.get(field_id)
        if not field:
            return None, "Field not found."

        if "farmer_id" in data and data["farmer_id"]:
            if not Farmer.query.get(data["farmer_id"]):
                return None, "Specified farmer does not exist."
            field.farmer_id = int(data["farmer_id"])

        if "field_name" in data and data["field_name"].strip():
            field.field_name = data["field_name"].strip()
        if "location" in data and data["location"].strip():
            field.location = data["location"].strip()
        if "area" in data and data["area"] is not None:
            try:
                area_val = float(data["area"])
                if area_val > 0:
                    field.area = area_val
            except (ValueError, TypeError):
                return None, "Field area must be a valid number."
        if "soil_type" in data and data["soil_type"].strip():
            field.soil_type = data["soil_type"].strip()

        db.session.commit()
        return field.to_dict(), None

    @staticmethod
    def delete(field_id: int):
        field = Field.query.get(field_id)
        if not field:
            return False, "Field not found."

        active_batches = [b for b in field.batches if b.status != "Harvested"]
        if active_batches:
            return False, f"Cannot delete field with active crop batches ({len(active_batches)} active batches present)."

        db.session.delete(field)
        db.session.commit()
        return True, None
