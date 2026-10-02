from sqlalchemy import func
from backend.database import db
from backend.models.farmer import Farmer
from backend.models.field import Field
from backend.models.crop import Crop
from backend.models.batch import CropBatch
from backend.models.activity import CultivationActivity
from backend.utils.validators import parse_date

class AnalyticsService:
    @staticmethod
    def get_dashboard_summary(farmer_id: int = None):
        """Fetch high-level KPI cards and chart data for the dashboard."""
        # Total counts
        total_farmers = (
            Farmer.query.count()
            if farmer_id is None
            else Farmer.query.filter_by(farmer_id=farmer_id).count()
        )
        
        field_query = Field.query
        if farmer_id is not None:
            field_query = field_query.filter_by(farmer_id=farmer_id)
        total_fields = field_query.count()

        batch_base = CropBatch.query.join(Field)
        if farmer_id is not None:
            batch_base = batch_base.filter(Field.farmer_id == farmer_id)

        all_batches = batch_base.all()
        active_batches = sum(1 for b in all_batches if b.status != "Harvested")
        completed_batches = sum(1 for b in all_batches if b.status == "Harvested")

        harvested_batches = [b for b in all_batches if b.status == "Harvested" and b.yield_amount and b.yield_amount > 0]
        total_production = sum(float(b.yield_amount) for b in harvested_batches)
        avg_yield = round(total_production / len(harvested_batches), 2) if harvested_batches else 0.0

        # 1. Batch Status Distribution
        status_counts = {
            "Planned": 0,
            "Planted": 0,
            "Growing": 0,
            "Ready for Harvest": 0,
            "Harvested": 0
        }
        for b in all_batches:
            if b.status in status_counts:
                status_counts[b.status] += 1

        # 2. Crop Production Chart (Total Production by Crop)
        crop_prod_map = {}
        for b in all_batches:
            crop_name = b.crop.crop_name if b.crop else "Unknown"
            y_val = float(b.yield_amount) if b.yield_amount else 0.0
            crop_prod_map[crop_name] = crop_prod_map.get(crop_name, 0.0) + y_val

        crop_production_chart = {
            "labels": list(crop_prod_map.keys()),
            "data": [round(v, 2) for v in crop_prod_map.values()]
        }

        # 3. Yield Trend Chart (Sorted chronologically by harvest or planting date)
        dated_batches = sorted(
            [b for b in all_batches if b.yield_amount and b.yield_amount > 0],
            key=lambda x: x.actual_harvest_date or x.planting_date
        )
        yield_trend_chart = {
            "labels": [(b.actual_harvest_date or b.planting_date).strftime("%b %Y") for b in dated_batches],
            "batch_codes": [b.batch_code for b in dated_batches],
            "data": [float(b.yield_amount) for b in dated_batches]
        }

        # 4. Resource Utilization Chart (Sum of quantities by activity type)
        activity_base = CultivationActivity.query.join(CropBatch).join(Field)
        if farmer_id is not None:
            activity_base = activity_base.filter(Field.farmer_id == farmer_id)

        activities = activity_base.all()
        activity_type_totals = {
            "Irrigation": 0.0,
            "Fertilization": 0.0,
            "Pest/Disease": 0.0,
            "Harvesting": 0.0
        }
        for a in activities:
            if a.activity_type in activity_type_totals:
                activity_type_totals[a.activity_type] += float(a.quantity_used or 0.0)

        resource_utilization_chart = {
            "labels": list(activity_type_totals.keys()),
            "data": [round(v, 2) for v in activity_type_totals.values()]
        }

        # Recent activities (last 5)
        recent_activities = activity_base.order_by(CultivationActivity.activity_date.desc(), CultivationActivity.activity_id.desc()).limit(6).all()

        return {
            "kpis": {
                "total_farmers": total_farmers,
                "total_fields": total_fields,
                "active_batches": active_batches,
                "completed_batches": completed_batches,
                "total_production": round(total_production, 2),
                "avg_yield": avg_yield
            },
            "batch_status_chart": {
                "labels": list(status_counts.keys()),
                "data": list(status_counts.values())
            },
            "crop_production_chart": crop_production_chart,
            "yield_trend_chart": yield_trend_chart,
            "resource_utilization_chart": resource_utilization_chart,
            "recent_activities": [a.to_dict() for a in recent_activities]
        }

    @staticmethod
    def get_detailed_reports(
        crop_id: int = None,
        farmer_id: int = None,
        field_id: int = None,
        date_from: str = None,
        date_to: str = None
    ):
        """Detailed multi-dimension analytics for the dedicated analytics portal."""
        query = CropBatch.query.join(Field).join(Crop).join(Farmer, Field.farmer_id == Farmer.farmer_id)

        if crop_id:
            query = query.filter(CropBatch.crop_id == crop_id)
        if field_id:
            query = query.filter(CropBatch.field_id == field_id)
        if farmer_id:
            query = query.filter(Field.farmer_id == farmer_id)

        d_from = parse_date(date_from)
        if d_from:
            query = query.filter(CropBatch.planting_date >= d_from)

        d_to = parse_date(date_to)
        if d_to:
            query = query.filter(CropBatch.planting_date <= d_to)

        batches = query.all()

        # Farmer-wise production
        farmer_production = {}
        for b in batches:
            f_name = b.field.farmer.name if b.field and b.field.farmer else "Unknown"
            farmer_production[f_name] = farmer_production.get(f_name, 0.0) + (float(b.yield_amount) if b.yield_amount else 0.0)

        # Field-wise production
        field_production = {}
        for b in batches:
            fld_name = b.field.field_name if b.field else "Unknown"
            field_production[fld_name] = field_production.get(fld_name, 0.0) + (float(b.yield_amount) if b.yield_amount else 0.0)

        # Crop-wise comparison: Expected Yield vs Actual Yield
        crop_comparison = {}
        for b in batches:
            c_name = b.crop.crop_name if b.crop else "Unknown"
            if c_name not in crop_comparison:
                crop_comparison[c_name] = {
                    "expected": float(b.crop.expected_yield) if b.crop and b.crop.expected_yield else 0.0,
                    "actual_sum": 0.0,
                    "count": 0
                }
            if b.yield_amount:
                crop_comparison[c_name]["actual_sum"] += float(b.yield_amount)
                crop_comparison[c_name]["count"] += 1

        crop_comparison_data = []
        for c_name, val in crop_comparison.items():
            avg_actual = round(val["actual_sum"] / val["count"], 2) if val["count"] > 0 else 0.0
            crop_comparison_data.append({
                "crop_name": c_name,
                "expected": val["expected"],
                "actual": avg_actual
            })

        return {
            "farmer_production": {
                "labels": list(farmer_production.keys()),
                "data": [round(v, 2) for v in farmer_production.values()]
            },
            "field_production": {
                "labels": list(field_production.keys()),
                "data": [round(v, 2) for v in field_production.values()]
            },
            "crop_comparison": crop_comparison_data,
            "total_batches_analyzed": len(batches)
        }
