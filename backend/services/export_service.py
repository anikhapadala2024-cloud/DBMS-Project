import io
import csv
from backend.models.batch import CropBatch
from backend.models.activity import CultivationActivity
from backend.models.field import Field
from backend.models.farmer import Farmer
from backend.models.crop import Crop

class ExportService:
    @staticmethod
    def export_batches_csv(crop_id=None, farmer_id=None, status=None):
        """Export filtered crop batches into CSV string."""
        query = CropBatch.query.join(Field).join(Crop).join(Farmer, Field.farmer_id == Farmer.farmer_id)

        if crop_id:
            query = query.filter(CropBatch.crop_id == crop_id)
        if farmer_id:
            query = query.filter(Field.farmer_id == farmer_id)
        if status and status != "All":
            query = query.filter(CropBatch.status == status)

        batches = query.order_by(CropBatch.batch_id.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Batch ID",
            "Batch Code",
            "Crop Name",
            "Crop Type",
            "Farmer Name",
            "Field Name",
            "Field Location",
            "Area (Acres)",
            "Planting Date",
            "Expected Harvest Date",
            "Actual Harvest Date",
            "Quantity Planted",
            "Harvested Yield",
            "Status",
            "Created At"
        ])

        for b in batches:
            fld = b.field
            farmer = fld.farmer if fld else None
            crp = b.crop
            writer.writerow([
                b.batch_id,
                b.batch_code,
                crp.crop_name if crp else "",
                crp.crop_type if crp else "",
                farmer.name if farmer else "",
                fld.field_name if fld else "",
                fld.location if fld else "",
                float(fld.area) if fld and fld.area else "",
                b.planting_date.strftime("%Y-%m-%d") if b.planting_date else "",
                b.expected_harvest_date.strftime("%Y-%m-%d") if b.expected_harvest_date else "",
                b.actual_harvest_date.strftime("%Y-%m-%d") if b.actual_harvest_date else "",
                float(b.quantity) if b.quantity is not None else 0.0,
                float(b.yield_amount) if b.yield_amount is not None else 0.0,
                b.status,
                b.created_at.strftime("%Y-%m-%d %H:%M:%S") if b.created_at else ""
            ])

        output.seek(0)
        return output.getvalue()

    @staticmethod
    def export_activities_csv(batch_id=None, activity_type=None, farmer_id=None):
        """Export cultivation activities into CSV format."""
        query = CultivationActivity.query.join(CropBatch)

        if farmer_id is not None:
            query = query.join(CropBatch.field).filter_by(farmer_id=farmer_id)

        if batch_id:
            query = query.filter(CultivationActivity.batch_id == batch_id)
        if activity_type and activity_type != "All":
            query = query.filter(CultivationActivity.activity_type == activity_type)

        activities = query.order_by(CultivationActivity.activity_date.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Activity ID",
            "Batch Code",
            "Crop",
            "Farmer",
            "Activity Type",
            "Activity Date",
            "Quantity Used",
            "Unit",
            "Description",
            "Logged At"
        ])

        for a in activities:
            b = a.batch
            f = b.field if b else None
            farmer = f.farmer if f else None
            c = b.crop if b else None

            writer.writerow([
                a.activity_id,
                b.batch_code if b else "",
                c.crop_name if c else "",
                farmer.name if farmer else "",
                a.activity_type,
                a.activity_date.strftime("%Y-%m-%d") if a.activity_date else "",
                float(a.quantity_used) if a.quantity_used is not None else 0.0,
                a.unit,
                a.description,
                a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else ""
            ])

        output.seek(0)
        return output.getvalue()
