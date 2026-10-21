import asyncio
from datetime import date
from sqlalchemy import select
from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.models.user import User, UserRole
from app.models.farm import Farm, Field, CropCycle
from app.models.soil import SoilRecord
from app.models.task import Task
from app.models.finance import Expense, Revenue
from app.models.machinery import Machinery
from app.models.scheme import SchemeRecord
from app.models.system import AiModelStat


async def seed_database():
    print("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        res = await session.execute(select(User).where(User.email == settings.ADMIN_EMAIL.lower()))
        admin = res.scalar_one_or_none()

        if not admin:
            print(f"Creating primary Admin user: {settings.ADMIN_EMAIL}...")
            admin = User(
                email=settings.ADMIN_EMAIL.lower(),
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                name=settings.ADMIN_NAME,
                role=UserRole.ADMIN,
                phone="+91 94311-84920",
                village="Jarga",
                district="Hazaribagh",
                state="Jharkhand",
                lat=24.002,
                lon=85.361,
                preferred_language="en"
            )
            session.add(admin)
            await session.flush()

            # Seed Farm
            farm = Farm(
                user_id=admin.id,
                name="Jarga Main Homestead Farm",
                total_area_acres=2.0,
                original_unit_value=64.0,
                original_unit_name="Katha (Jharkhand 32 Katha/Acre)",
                tenure="Owned",
                location="Jarga, Hazaribagh, Jharkhand",
                lat=24.002,
                lon=85.361
            )
            session.add(farm)
            await session.flush()

            # Seed 3 Fields
            f1 = Field(farm_id=farm.id, name="Plot A — North Lowland (Don-2)", code="FLD-01", area_acres=1.1, area_hectares=0.445, soil_type="Clay Loam (pH 6.1)", water_source="Solar Borewell + Check Dam", lat=24.002, lon=85.361)
            f2 = Field(farm_id=farm.id, name="Plot B — East Mid-Upland (Tanr-1)", code="FLD-02", area_acres=0.6, area_hectares=0.243, soil_type="Sandy Loam (pH 6.3)", water_source="Rainfed + Farm Pond Drip", lat=24.003, lon=85.362)
            f3 = Field(farm_id=farm.id, name="Plot C — South Vegetable Block", code="FLD-03", area_acres=0.3, area_hectares=0.121, soil_type="Rich Loam (pH 6.6)", water_source="Solar Drip Line", lat=24.001, lon=85.360)
            session.add_all([f1, f2, f3])
            await session.flush()

            # Seed Crop Cycles
            c1 = CropCycle(field_id=f1.id, crop_name="Paddy", variety="Sahbhagi Dhan", season="Kharif 2025", sowing_date=date(2025, 5, 9), stage="Active Tillering / Panicle Initiation", expected_yield_qtl=24.5, expected_profit_inr=72400.0)
            c2 = CropCycle(field_id=f2.id, crop_name="Paddy", variety="IR-64 Drt1", season="Kharif 2025", sowing_date=date(2025, 5, 14), stage="Mid-Tillering", expected_yield_qtl=13.2, expected_profit_inr=36800.0)
            c3 = CropCycle(field_id=f3.id, crop_name="Hybrid Tomato", variety="Arka Rakshak F1", season="Kharif 2025", sowing_date=date(2025, 5, 20), stage="Flowering & Fruit Set", expected_yield_qtl=18.0, expected_profit_inr=15800.0)
            session.add_all([c1, c2, c3])

            # Seed Soil Card
            soil = SoilRecord(
                user_id=admin.id,
                field_name="Plot A — North Lowland",
                sample_id="SHC-JH-HZB-2025-0891",
                sample_date=date(2025, 4, 18),
                source_type="Lab-Measured (Soil Health Card Verified)",
                is_verified=True,
                ph=6.1,
                ec=0.28,
                organic_carbon_pct=0.58,
                nitrogen_kg_ha=218.0,
                phosphorus_kg_ha=19.4,
                potassium_kg_ha=184.0,
                zinc_ppm=0.52,
                boron_ppm=0.41,
                sulphur_ppm=11.2
            )
            session.add(soil)

            # Seed Tasks
            t1 = Task(user_id=admin.id, title="Urea Application", description="Apply 2nd dose of neem-coated urea (28 kg/acre) after rain window", due_date=date(2025, 6, 25), field_name="Plot A — North Lowland", category="Nutrient", priority="High")
            t2 = Task(user_id=admin.id, title="Weed Control", description="Manual cono-weeder pass required between paddy rows", due_date=date(2025, 6, 26), field_name="Plot A & Plot B", category="Weed-Control", priority="Medium")
            t3 = Task(user_id=admin.id, title="Bund & Spillway Check", description="Inspect North Lowland bunds before Tuesday heavy rain", due_date=date(2025, 6, 23), field_name="Plot A — North Lowland", category="Irrigation", priority="High")
            session.add_all([t1, t2, t3])

            # Seed Machinery
            m1 = Machinery(user_id=admin.id, name="Power Tiller (12 HP VST Shakti)", mode="Owned", cost_per_hr=280.0, custom_hire_rate_hr=650.0, hours_used_season=38.0, fuel_litres_hr=1.4, next_service="After 12 hrs")
            m2 = Machinery(user_id=admin.id, name="Solar Submersible Pump (3 HP DC)", mode="Owned (PM-KUSUM)", cost_per_hr=15.0, custom_hire_rate_hr=180.0, hours_used_season=95.0, fuel_litres_hr=0.0, next_service="Panel Clean Weekly")
            session.add_all([m1, m2])

            await session.commit()
            print("Database seeded with Admin, Farm, Fields, Crops, Soil, and Tasks successfully!")
        else:
            print("Database already contains Admin user. Skipping seed.")


if __name__ == "__main__":
    asyncio.run(seed_database())
