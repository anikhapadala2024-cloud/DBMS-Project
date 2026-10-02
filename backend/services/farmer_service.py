from backend.database import db
from backend.models.farmer import Farmer
from backend.models.field import Field
from backend.models.batch import CropBatch
from sqlalchemy import or_

class FarmerService:
    @staticmethod
    def get_all(search: str = None, page: int = 1, limit: int = 10, farmer_user_id: int = None):
        query = Farmer.query

        if farmer_user_id is not None:
            query = query.filter_by(user_id=farmer_user_id)

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Farmer.name.ilike(term),
                    Farmer.phone.ilike(term),
                    Farmer.village.ilike(term),
                    Farmer.address.ilike(term)
                )
            )

        total = query.count()
        query = query.order_by(Farmer.farmer_id.desc())

        if limit and limit > 0:
            farmers = query.offset((page - 1) * limit).limit(limit).all()
        else:
            farmers = query.all()

        return {
            "farmers": [f.to_dict() for f in farmers],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 1
        }

    @staticmethod
    def get_by_id(farmer_id: int):
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return None
        data = farmer.to_dict()
        data["fields"] = [f.to_dict() for f in farmer.fields]
        return data

    @staticmethod
    def create(data: dict):
        name = data.get("name")
        phone = data.get("phone")
        address = data.get("address")
        village = data.get("village")

        if not name or not name.strip():
            return None, "Farmer name is required."
        if not phone or not phone.strip():
            return None, "Phone number is required."
        if not address or not address.strip():
            return None, "Address is required."
        if not village or not village.strip():
            return None, "Village name is required."

        farmer = Farmer(
            name=name.strip(),
            phone=phone.strip(),
            address=address.strip(),
            village=village.strip(),
            user_id=data.get("user_id")
        )
        db.session.add(farmer)
        db.session.commit()
        return farmer.to_dict(), None

    @staticmethod
    def update(farmer_id: int, data: dict):
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return None, "Farmer not found."

        if "name" in data and data["name"].strip():
            farmer.name = data["name"].strip()
        if "phone" in data and data["phone"].strip():
            farmer.phone = data["phone"].strip()
        if "address" in data and data["address"].strip():
            farmer.address = data["address"].strip()
        if "village" in data and data["village"].strip():
            farmer.village = data["village"].strip()

        db.session.commit()
        return farmer.to_dict(), None

    @staticmethod
    def delete(farmer_id: int):
        farmer = Farmer.query.get(farmer_id)
        if not farmer:
            return False, "Farmer not found."

        # Check if farmer has active batches
        for f in farmer.fields:
            active_batches = [b for b in f.batches if b.status != "Harvested"]
            if active_batches:
                return False, f"Cannot delete farmer with active crop batches in field '{f.field_name}'."

        db.session.delete(farmer)
        db.session.commit()
        return True, None
