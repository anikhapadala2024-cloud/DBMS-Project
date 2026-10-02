import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()

def ensure_mysql_database_exists():
    """Ensure that the agritech_db database exists on the MySQL server."""
    try:
        # Connect to MySQL server without database specified
        if Config.DB_PASSWORD:
            server_uri = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/?charset=utf8mb4"
        else:
            server_uri = f"mysql+pymysql://{Config.DB_USER}@{Config.DB_HOST}:{Config.DB_PORT}/?charset=utf8mb4"
        
        engine = create_engine(server_uri, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
            conn.commit()
        logger.info(f"Database `{Config.DB_NAME}` verified/created on MySQL server.")
        return True
    except Exception as e:
        logger.warning(f"Unable to connect to MySQL server to ensure database: {e}")
        return False

def init_db(app):
    """
    Initialize SQLAlchemy database connection.
    Attempts MySQL first; falls back to SQLite if MySQL is offline and fallback is permitted.
    """
    mysql_ready = ensure_mysql_database_exists()
    used_engine = "mysql"

    if mysql_ready:
        app.config["SQLALCHEMY_DATABASE_URI"] = Config.get_mysql_uri()
        logger.info(f"Using MySQL Database: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
    elif Config.ALLOW_SQLITE_FALLBACK:
        app.config["SQLALCHEMY_DATABASE_URI"] = Config.get_sqlite_uri()
        used_engine = "sqlite"
        logger.warning(
            "MySQL was not reachable. Using SQLite fallback for offline viva/presentation.\n"
            f"SQLite DB located at: {Config.get_sqlite_uri()}"
        )
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = Config.get_mysql_uri()
        logger.error("MySQL is unreachable and SQLite fallback is disabled.")

    db.init_app(app)

    with app.app_context():
        # Import models so they are registered with SQLAlchemy
        from backend.models import User, Farmer, Field, Crop, CropBatch, CultivationActivity
        db.create_all()
        logger.info("Database tables verified.")

        # Seed initial data if empty
        seed_database_if_empty()

    return used_engine

def seed_database_if_empty():
    """Seed initial sample data if the users or crops table is empty."""
    from backend.models import User, Farmer, Field, Crop, CropBatch, CultivationActivity
    from werkzeug.security import generate_password_hash
    from datetime import date, datetime

    if User.query.count() > 0:
        logger.info("Database already contains data; skipping automatic seeding.")
        return

    logger.info("Seeding initial realistic agricultural data...")

    try:
        # 1. Users
        admin_user = User(
            name="AgriTech Admin",
            email="admin@agritech.com",
            password=generate_password_hash("Admin@123"),
            role="admin"
        )
        farmer_user_1 = User(
            name="Ramesh Kumar Patel",
            email="farmer.ramesh@agritech.com",
            password=generate_password_hash("Farmer@123"),
            role="farmer"
        )
        farmer_user_2 = User(
            name="Suresh Chandra Sharma",
            email="farmer.suresh@agritech.com",
            password=generate_password_hash("Farmer@123"),
            role="farmer"
        )
        farmer_user_3 = User(
            name="Priya Devi Verma",
            email="farmer.priya@agritech.com",
            password=generate_password_hash("Farmer@123"),
            role="farmer"
        )
        farmer_user_4 = User(
            name="Anita Bai Singh",
            email="farmer.anita@agritech.com",
            password=generate_password_hash("Farmer@123"),
            role="farmer"
        )
        farmer_user_5 = User(
            name="Rajesh Mohan Deshmukh",
            email="farmer.rajesh@agritech.com",
            password=generate_password_hash("Farmer@123"),
            role="farmer"
        )

        db.session.add_all([admin_user, farmer_user_1, farmer_user_2, farmer_user_3, farmer_user_4, farmer_user_5])
        db.session.commit()

        # 2. Farmers (5 Farmers)
        farmer_1 = Farmer(user_id=farmer_user_1.id, name="Ramesh Kumar Patel", phone="+91 98261 45012", address="House No. 24, Canal Road", village="Greenfield Agro Colony")
        farmer_2 = Farmer(user_id=farmer_user_2.id, name="Suresh Chandra Sharma", phone="+91 94140 28931", address="Plot 5B, Temple Street", village="Kisan Nagar")
        farmer_3 = Farmer(user_id=farmer_user_3.id, name="Priya Devi Verma", phone="+91 87654 11980", address="Near Primary School, Ward 3", village="Sundarpur")
        farmer_4 = Farmer(user_id=farmer_user_4.id, name="Anita Bai Singh", phone="+91 91234 56789", address="Farm House 12, River Belt", village="Anandpur")
        farmer_5 = Farmer(user_id=farmer_user_5.id, name="Rajesh Mohan Deshmukh", phone="+91 99887 65432", address="National Highway Bypass", village="Navgaon")

        db.session.add_all([farmer_1, farmer_2, farmer_3, farmer_4, farmer_5])
        db.session.commit()

        # 3. Fields (6 Fields)
        f1 = Field(farmer_id=farmer_1.farmer_id, field_name="North Meadow - Plot A", location="North Ridge Sector 1", area=12.50, soil_type="Alluvial")
        f2 = Field(farmer_id=farmer_1.farmer_id, field_name="Canal View - Plot B", location="East Canal Basin", area=8.00, soil_type="Loamy")
        f3 = Field(farmer_id=farmer_2.farmer_id, field_name="Valley Sunshine Field", location="Valley Floor West", area=15.00, soil_type="Black")
        f4 = Field(farmer_id=farmer_3.farmer_id, field_name="Sundarpur Terraces", location="Hill Slope South", area=6.50, soil_type="Red")
        f5 = Field(farmer_id=farmer_4.farmer_id, field_name="Riverbank Fertile Basin", location="Riverbed North Zone", area=18.00, soil_type="Clay Loam")
        f6 = Field(farmer_id=farmer_5.farmer_id, field_name="Navgaon Highfield", location="Highway Corridor Block 4", area=10.00, soil_type="Sandy Loam")

        db.session.add_all([f1, f2, f3, f4, f5, f6])
        db.session.commit()

        # 4. Crops (6 Crops)
        c1 = Crop(crop_name="Golden Sharbati Wheat", crop_type="Cereal", season="Rabi", expected_yield=22.50)
        c2 = Crop(crop_name="Basmati Paddy (Rice)", crop_type="Cereal", season="Kharif", expected_yield=28.00)
        c3 = Crop(crop_name="Sweet Yellow Corn (Maize)", crop_type="Cereal", season="Kharif", expected_yield=32.00)
        c4 = Crop(crop_name="Black Gold Soybean", crop_type="Pulse", season="Kharif", expected_yield=14.50)
        c5 = Crop(crop_name="Long Staple BT Cotton", crop_type="Cash Crop", season="Kharif", expected_yield=12.00)
        c6 = Crop(crop_name="Hybrid Roma Tomato", crop_type="Vegetable", season="Year-Round", expected_yield=45.00)

        db.session.add_all([c1, c2, c3, c4, c5, c6])
        db.session.commit()

        # 5. Crop Batches (10 Batches)
        b1 = CropBatch(
            field_id=f1.field_id, crop_id=c1.crop_id, batch_code="BATCH-2025-WHT01",
            planting_date=date(2025, 11, 10), expected_harvest_date=date(2026, 3, 25), actual_harvest_date=date(2026, 3, 24),
            quantity=500.0, yield_amount=275.0, status="Harvested"
        )
        b2 = CropBatch(
            field_id=f2.field_id, crop_id=c6.crop_id, batch_code="BATCH-2025-TOM01",
            planting_date=date(2025, 12, 5), expected_harvest_date=date(2026, 2, 28), actual_harvest_date=date(2026, 3, 2),
            quantity=200.0, yield_amount=350.0, status="Harvested"
        )
        b3 = CropBatch(
            field_id=f3.field_id, crop_id=c4.crop_id, batch_code="BATCH-2026-SOY01",
            planting_date=date(2026, 6, 15), expected_harvest_date=date(2026, 10, 10),
            quantity=600.0, yield_amount=0.0, status="Growing"
        )
        b4 = CropBatch(
            field_id=f4.field_id, crop_id=c2.crop_id, batch_code="BATCH-2026-RIC01",
            planting_date=date(2026, 6, 20), expected_harvest_date=date(2026, 10, 25),
            quantity=300.0, yield_amount=0.0, status="Growing"
        )
        b5 = CropBatch(
            field_id=f5.field_id, crop_id=c5.crop_id, batch_code="BATCH-2026-COT01",
            planting_date=date(2026, 5, 18), expected_harvest_date=date(2026, 11, 15),
            quantity=450.0, yield_amount=0.0, status="Ready for Harvest"
        )
        b6 = CropBatch(
            field_id=f6.field_id, crop_id=c3.crop_id, batch_code="BATCH-2026-MAZ01",
            planting_date=date(2026, 7, 1), expected_harvest_date=date(2026, 10, 15),
            quantity=400.0, yield_amount=0.0, status="Growing"
        )
        b7 = CropBatch(
            field_id=f1.field_id, crop_id=c2.crop_id, batch_code="BATCH-2026-RIC02",
            planting_date=date(2026, 7, 10), expected_harvest_date=date(2026, 11, 5),
            quantity=550.0, yield_amount=0.0, status="Planted"
        )
        b8 = CropBatch(
            field_id=f2.field_id, crop_id=c6.crop_id, batch_code="BATCH-2026-TOM02",
            planting_date=date(2026, 8, 1), expected_harvest_date=date(2026, 10, 30),
            quantity=250.0, yield_amount=0.0, status="Planted"
        )
        b9 = CropBatch(
            field_id=f3.field_id, crop_id=c1.crop_id, batch_code="BATCH-2026-WHT02",
            planting_date=date(2026, 11, 1), expected_harvest_date=date(2027, 3, 15),
            quantity=650.0, yield_amount=0.0, status="Planned"
        )
        b10 = CropBatch(
            field_id=f5.field_id, crop_id=c3.crop_id, batch_code="BATCH-2026-MAZ02",
            planting_date=date(2026, 10, 20), expected_harvest_date=date(2027, 2, 10),
            quantity=500.0, yield_amount=0.0, status="Planned"
        )

        db.session.add_all([b1, b2, b3, b4, b5, b6, b7, b8, b9, b10])
        db.session.commit()

        # 6. Cultivation Activities (22 Activities)
        activities = [
            # Batch 1
            CultivationActivity(batch_id=b1.batch_id, activity_type="Irrigation", activity_date=date(2025, 11, 15), description="Initial soaking irrigation after sowing seeds", quantity_used=4500.0, unit="Liters"),
            CultivationActivity(batch_id=b1.batch_id, activity_type="Fertilization", activity_date=date(2025, 12, 5), description="Application of NPK 12-32-16 basal fertilizer", quantity_used=150.0, unit="Kg"),
            CultivationActivity(batch_id=b1.batch_id, activity_type="Irrigation", activity_date=date(2026, 1, 10), description="Crown root stage flood irrigation", quantity_used=6000.0, unit="Liters"),
            CultivationActivity(batch_id=b1.batch_id, activity_type="Pest/Disease", activity_date=date(2026, 1, 28), description="Preventive spraying for yellow rust disease using Propiconazole", quantity_used=2.5, unit="Liters"),
            CultivationActivity(batch_id=b1.batch_id, activity_type="Harvesting", activity_date=date(2026, 3, 24), description="Combine harvester operation for prime Sharbati grain", quantity_used=275.0, unit="Quintals"),
            # Batch 2
            CultivationActivity(batch_id=b2.batch_id, activity_type="Irrigation", activity_date=date(2025, 12, 8), description="Drip irrigation for transplanted seedling establishment", quantity_used=1200.0, unit="Liters"),
            CultivationActivity(batch_id=b2.batch_id, activity_type="Fertilization", activity_date=date(2025, 12, 24), description="Water soluble Calcium Nitrate fertigation", quantity_used=35.0, unit="Kg"),
            CultivationActivity(batch_id=b2.batch_id, activity_type="Pest/Disease", activity_date=date(2026, 1, 15), description="Organic neem oil spray against whitefly and aphids", quantity_used=5.0, unit="Liters"),
            CultivationActivity(batch_id=b2.batch_id, activity_type="Harvesting", activity_date=date(2026, 3, 2), description="Manual hand picking of first grade red tomatoes", quantity_used=350.0, unit="Crates"),
            # Batch 3
            CultivationActivity(batch_id=b3.batch_id, activity_type="Irrigation", activity_date=date(2026, 6, 25), description="Early vegetative irrigation post germination", quantity_used=5000.0, unit="Liters"),
            CultivationActivity(batch_id=b3.batch_id, activity_type="Fertilization", activity_date=date(2026, 7, 12), description="DAP and Rhizobium culture soil broadcast", quantity_used=120.0, unit="Kg"),
            CultivationActivity(batch_id=b3.batch_id, activity_type="Pest/Disease", activity_date=date(2026, 8, 4), description="Monocrotophos spray against stem fly infestation", quantity_used=3.0, unit="Liters"),
            # Batch 4
            CultivationActivity(batch_id=b4.batch_id, activity_type="Irrigation", activity_date=date(2026, 6, 28), description="Paddy field ponding water depth maintained to 5cm", quantity_used=8500.0, unit="Liters"),
            CultivationActivity(batch_id=b4.batch_id, activity_type="Fertilization", activity_date=date(2026, 7, 18), description="Urea top dressing at tillering stage", quantity_used=90.0, unit="Kg"),
            CultivationActivity(batch_id=b4.batch_id, activity_type="Pest/Disease", activity_date=date(2026, 8, 10), description="Chlorantraniliprole treatment for stem borer", quantity_used=1.8, unit="Liters"),
            # Batch 5
            CultivationActivity(batch_id=b5.batch_id, activity_type="Irrigation", activity_date=date(2026, 5, 25), description="Alternate furrow irrigation during square formation", quantity_used=4000.0, unit="Liters"),
            CultivationActivity(batch_id=b5.batch_id, activity_type="Fertilization", activity_date=date(2026, 6, 30), description="Potassium Schoenite and Zinc Sulphate foliar nutrition", quantity_used=45.0, unit="Kg"),
            CultivationActivity(batch_id=b5.batch_id, activity_type="Pest/Disease", activity_date=date(2026, 7, 25), description="Bollworm scouting and pheromone trap deployment", quantity_used=15.0, unit="Traps"),
            CultivationActivity(batch_id=b5.batch_id, activity_type="Pest/Disease", activity_date=date(2026, 8, 20), description="Biocontrol Trichogramma card release", quantity_used=10.0, unit="Cards"),
            # Batch 6
            CultivationActivity(batch_id=b6.batch_id, activity_type="Irrigation", activity_date=date(2026, 7, 15), description="Sprinkler irrigation at knee-high stage", quantity_used=3500.0, unit="Liters"),
            CultivationActivity(batch_id=b6.batch_id, activity_type="Fertilization", activity_date=date(2026, 8, 2), description="Secondary nitrogen boost with granular ammonium sulphate", quantity_used=75.0, unit="Kg"),
            # Batch 7
            CultivationActivity(batch_id=b7.batch_id, activity_type="Irrigation", activity_date=date(2026, 7, 14), description="Nursery transplant bed saturation", quantity_used=3000.0, unit="Liters")
        ]

        db.session.add_all(activities)
        db.session.commit()
        logger.info("Database seeding completed successfully!")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding database: {e}")
