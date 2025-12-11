import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "maritime-demurrage-key")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from models import init_models
models = init_models(db)
Vessel = models['Vessel']
VesselType = models['VesselType']
Port = models['Port']
CargoType = models['CargoType']
Voyage = models['Voyage']
DemurrageRecord = models['DemurrageRecord']

from ontology import MaritimeOntology
from demurrage_model import DemurragePredictor

ontology = MaritimeOntology()
predictor = DemurragePredictor()

@app.route("/")
def dashboard():
    vessels = Vessel.query.all()
    ports = Port.query.all()
    voyages = Voyage.query.order_by(Voyage.created_at.desc()).limit(10).all()
    
    total_demurrage = db.session.query(db.func.sum(DemurrageRecord.cost)).scalar() or 0
    total_voyages = Voyage.query.count()
    avg_delay = db.session.query(db.func.avg(DemurrageRecord.delay_hours)).scalar() or 0
    
    return render_template("dashboard.html", 
                         vessels=vessels, 
                         ports=ports, 
                         voyages=voyages,
                         total_demurrage=total_demurrage,
                         total_voyages=total_voyages,
                         avg_delay=round(avg_delay, 1))

@app.route("/voyage/plan", methods=["GET", "POST"])
def voyage_planning():
    vessels = Vessel.query.all()
    ports = Port.query.all()
    cargo_types = CargoType.query.all()
    
    prediction = None
    if request.method == "POST":
        vessel_id = request.form.get("vessel_id")
        origin_port_id = request.form.get("origin_port_id")
        dest_port_id = request.form.get("dest_port_id")
        cargo_type_id = request.form.get("cargo_type_id")
        cargo_volume_str = request.form.get("cargo_volume", "0")
        cargo_volume = float(cargo_volume_str) if cargo_volume_str else 0
        eta_str = request.form.get("eta")
        
        vessel = Vessel.query.get(vessel_id)
        origin = Port.query.get(origin_port_id) if origin_port_id else None
        dest = Port.query.get(dest_port_id)
        cargo = CargoType.query.get(cargo_type_id)
        
        eta = datetime.strptime(eta_str, "%Y-%m-%dT%H:%M") if eta_str else datetime.utcnow()
        
        prediction = predictor.predict_demurrage(
            vessel=vessel,
            origin_port=origin,
            dest_port=dest,
            cargo_type=cargo,
            cargo_volume=cargo_volume,
            eta=eta,
            ontology=ontology
        )
        
        voyage = Voyage(
            vessel_id=vessel_id,
            origin_port_id=origin_port_id if origin_port_id else None,
            destination_port_id=dest_port_id,
            cargo_type_id=cargo_type_id,
            cargo_volume=cargo_volume,
            eta=eta,
            predicted_delay_hours=prediction["predicted_delay_hours"],
            predicted_demurrage_cost=prediction["predicted_cost"]
        )
        db.session.add(voyage)
        db.session.commit()
    
    return render_template("voyage_planning.html", 
                         vessels=vessels, 
                         ports=ports, 
                         cargo_types=cargo_types,
                         prediction=prediction)

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.json
    
    vessel = Vessel.query.get(data.get("vessel_id"))
    origin = Port.query.get(data.get("origin_port_id"))
    dest = Port.query.get(data.get("dest_port_id"))
    cargo = CargoType.query.get(data.get("cargo_type_id"))
    cargo_volume_val = data.get("cargo_volume", 0)
    cargo_volume = float(cargo_volume_val) if cargo_volume_val else 0
    eta_str = data.get("eta")
    
    eta = datetime.strptime(eta_str, "%Y-%m-%dT%H:%M") if eta_str else datetime.utcnow()
    
    prediction = predictor.predict_demurrage(
        vessel=vessel,
        origin_port=origin,
        dest_port=dest,
        cargo_type=cargo,
        cargo_volume=cargo_volume,
        eta=eta,
        ontology=ontology
    )
    
    return jsonify(prediction)

@app.route("/api/optimization", methods=["POST"])
def api_optimization():
    data = request.json
    
    vessel = Vessel.query.get(data.get("vessel_id"))
    dest = Port.query.get(data.get("dest_port_id"))
    cargo = CargoType.query.get(data.get("cargo_type_id"))
    cargo_volume_val = data.get("cargo_volume", 0)
    cargo_volume = float(cargo_volume_val) if cargo_volume_val else 0
    
    recommendations = predictor.get_optimization_recommendations(
        vessel=vessel,
        dest_port=dest,
        cargo_type=cargo,
        cargo_volume=cargo_volume,
        ontology=ontology
    )
    
    return jsonify(recommendations)

@app.route("/analytics")
def analytics():
    demurrage_by_port = db.session.query(
        Port.name,
        db.func.sum(DemurrageRecord.cost).label("total_cost"),
        db.func.avg(DemurrageRecord.delay_hours).label("avg_delay")
    ).join(Voyage, Voyage.destination_port_id == Port.id)\
     .join(DemurrageRecord, DemurrageRecord.voyage_id == Voyage.id)\
     .group_by(Port.name).all()
    
    demurrage_by_vessel = db.session.query(
        Vessel.name,
        db.func.sum(DemurrageRecord.cost).label("total_cost"),
        db.func.count(DemurrageRecord.id).label("incidents")
    ).join(Voyage, Voyage.vessel_id == Vessel.id)\
     .join(DemurrageRecord, DemurrageRecord.voyage_id == Voyage.id)\
     .group_by(Vessel.name).all()
    
    monthly_trend = db.session.query(
        db.func.date_trunc('month', DemurrageRecord.recorded_at).label("month"),
        db.func.sum(DemurrageRecord.cost).label("total_cost")
    ).group_by("month").order_by("month").all()
    
    return render_template("analytics.html",
                         demurrage_by_port=demurrage_by_port,
                         demurrage_by_vessel=demurrage_by_vessel,
                         monthly_trend=monthly_trend)

@app.route("/ontology")
def ontology_view():
    vessel_types = ontology.get_vessel_types()
    port_capabilities = ontology.get_port_capabilities()
    cargo_relationships = ontology.get_cargo_relationships()
    
    return render_template("ontology.html",
                         vessel_types=vessel_types,
                         port_capabilities=port_capabilities,
                         cargo_relationships=cargo_relationships)

@app.route("/fleet")
def fleet_management():
    vessels = Vessel.query.all()
    return render_template("fleet.html", vessels=vessels)

@app.route("/ports")
def port_management():
    ports = Port.query.all()
    return render_template("ports.html", ports=ports)

def seed_database():
    if Vessel.query.first() is not None:
        return
    
    from datetime import datetime, timedelta
    import random
    
    vessel_types_data = [
        {"name": "Bulk Carrier", "category": "dry_bulk", "typical_dwt_min": 10000, "typical_dwt_max": 400000, "loading_rate_factor": 1.0},
        {"name": "Tanker", "category": "liquid", "typical_dwt_min": 5000, "typical_dwt_max": 500000, "loading_rate_factor": 1.2},
        {"name": "Container Ship", "category": "containerized", "typical_dwt_min": 5000, "typical_dwt_max": 200000, "loading_rate_factor": 0.8},
        {"name": "General Cargo", "category": "break_bulk", "typical_dwt_min": 2000, "typical_dwt_max": 50000, "loading_rate_factor": 0.6},
    ]
    
    vessel_types = {}
    for vt_data in vessel_types_data:
        vt = VesselType(**vt_data)
        db.session.add(vt)
        db.session.flush()
        vessel_types[vt_data["name"]] = vt
    
    vessels_data = [
        {"name": "MV Pacific Trader", "imo_number": "IMO9123456", "vessel_type": "Bulk Carrier", "dwt": 75000, "loa": 225, "beam": 32, "draft": 14.5, "demurrage_rate": 28000},
        {"name": "MV Atlantic Fortune", "imo_number": "IMO9234567", "vessel_type": "Bulk Carrier", "dwt": 180000, "loa": 292, "beam": 45, "draft": 18.2, "demurrage_rate": 45000},
        {"name": "MT Ocean Spirit", "imo_number": "IMO9345678", "vessel_type": "Tanker", "dwt": 150000, "loa": 274, "beam": 48, "draft": 17.0, "demurrage_rate": 55000},
        {"name": "MT Gulf Star", "imo_number": "IMO9456789", "vessel_type": "Tanker", "dwt": 310000, "loa": 333, "beam": 60, "draft": 22.5, "demurrage_rate": 85000},
        {"name": "MV Container Express", "imo_number": "IMO9567890", "vessel_type": "Container Ship", "dwt": 65000, "loa": 294, "beam": 32, "draft": 13.5, "demurrage_rate": 35000},
        {"name": "MV Global Carrier", "imo_number": "IMO9678901", "vessel_type": "General Cargo", "dwt": 25000, "loa": 170, "beam": 25, "draft": 10.5, "demurrage_rate": 18000},
        {"name": "MV Iron Giant", "imo_number": "IMO9789012", "vessel_type": "Bulk Carrier", "dwt": 250000, "loa": 330, "beam": 57, "draft": 21.0, "demurrage_rate": 65000},
        {"name": "MT Petro Voyager", "imo_number": "IMO9890123", "vessel_type": "Tanker", "dwt": 80000, "loa": 244, "beam": 42, "draft": 14.8, "demurrage_rate": 40000},
    ]
    
    vessels = []
    for v_data in vessels_data:
        vessel = Vessel(
            name=v_data["name"],
            imo_number=v_data["imo_number"],
            vessel_type_id=vessel_types[v_data["vessel_type"]].id,
            dwt=v_data["dwt"],
            loa=v_data["loa"],
            beam=v_data["beam"],
            draft=v_data["draft"],
            demurrage_rate=v_data["demurrage_rate"]
        )
        db.session.add(vessel)
        vessels.append(vessel)
    
    ports_data = [
        {"name": "Port of Rotterdam", "code": "NLRTM", "country": "Netherlands", "latitude": 51.9, "longitude": 4.5, "avg_congestion_level": 0.65, "avg_berth_wait_hours": 18, "num_berths": 25, "max_draft": 24.0, "cargo_handling_rate": 12000, "weather_delay_factor": 1.1},
        {"name": "Port of Singapore", "code": "SGSIN", "country": "Singapore", "latitude": 1.3, "longitude": 103.8, "avg_congestion_level": 0.7, "avg_berth_wait_hours": 12, "num_berths": 40, "max_draft": 20.0, "cargo_handling_rate": 15000, "weather_delay_factor": 0.8},
        {"name": "Port of Shanghai", "code": "CNSHA", "country": "China", "latitude": 31.2, "longitude": 121.5, "avg_congestion_level": 0.75, "avg_berth_wait_hours": 24, "num_berths": 35, "max_draft": 18.0, "cargo_handling_rate": 10000, "weather_delay_factor": 1.0},
        {"name": "Port of Houston", "code": "USHOU", "country": "USA", "latitude": 29.8, "longitude": -95.3, "avg_congestion_level": 0.55, "avg_berth_wait_hours": 14, "num_berths": 18, "max_draft": 14.0, "cargo_handling_rate": 8000, "weather_delay_factor": 1.2},
        {"name": "Port of Santos", "code": "BRSSZ", "country": "Brazil", "latitude": -23.9, "longitude": -46.3, "avg_congestion_level": 0.6, "avg_berth_wait_hours": 20, "num_berths": 12, "max_draft": 14.5, "cargo_handling_rate": 6000, "weather_delay_factor": 0.9},
        {"name": "Port Hedland", "code": "AUPHE", "country": "Australia", "latitude": -20.3, "longitude": 118.6, "avg_congestion_level": 0.5, "avg_berth_wait_hours": 8, "num_berths": 6, "max_draft": 19.0, "cargo_handling_rate": 14000, "weather_delay_factor": 1.3},
        {"name": "Port of Fujairah", "code": "AEFJR", "country": "UAE", "latitude": 25.1, "longitude": 56.4, "avg_congestion_level": 0.45, "avg_berth_wait_hours": 6, "num_berths": 10, "max_draft": 18.0, "cargo_handling_rate": 11000, "weather_delay_factor": 0.7},
        {"name": "Port of Durban", "code": "ZADUR", "country": "South Africa", "latitude": -29.9, "longitude": 31.0, "avg_congestion_level": 0.68, "avg_berth_wait_hours": 22, "num_berths": 8, "max_draft": 12.8, "cargo_handling_rate": 5000, "weather_delay_factor": 1.1},
        {"name": "Port of Antwerp", "code": "BEANR", "country": "Belgium", "latitude": 51.2, "longitude": 4.4, "avg_congestion_level": 0.58, "avg_berth_wait_hours": 16, "num_berths": 20, "max_draft": 16.0, "cargo_handling_rate": 9000, "weather_delay_factor": 1.0},
        {"name": "Port of Busan", "code": "KRPUS", "country": "South Korea", "latitude": 35.1, "longitude": 129.0, "avg_congestion_level": 0.62, "avg_berth_wait_hours": 10, "num_berths": 22, "max_draft": 17.0, "cargo_handling_rate": 13000, "weather_delay_factor": 1.1},
    ]
    
    ports = []
    for p_data in ports_data:
        port = Port(**p_data)
        db.session.add(port)
        ports.append(port)
    
    cargo_types_data = [
        {"name": "Iron Ore", "category": "dry_bulk", "handling_complexity": 0.8, "requires_special_equipment": False, "is_hazardous": False, "typical_loading_rate": 8000},
        {"name": "Coal", "category": "dry_bulk", "handling_complexity": 0.9, "requires_special_equipment": False, "is_hazardous": False, "typical_loading_rate": 6000},
        {"name": "Grain", "category": "dry_bulk", "handling_complexity": 1.0, "requires_special_equipment": False, "is_hazardous": False, "typical_loading_rate": 5000},
        {"name": "Crude Oil", "category": "liquid_bulk", "handling_complexity": 1.2, "requires_special_equipment": True, "is_hazardous": True, "typical_loading_rate": 10000},
        {"name": "Refined Products", "category": "liquid_bulk", "handling_complexity": 1.1, "requires_special_equipment": True, "is_hazardous": True, "typical_loading_rate": 8000},
        {"name": "Containers", "category": "containerized", "handling_complexity": 0.7, "requires_special_equipment": True, "is_hazardous": False, "typical_loading_rate": 30},
        {"name": "LNG", "category": "liquid_bulk", "handling_complexity": 2.0, "requires_special_equipment": True, "is_hazardous": True, "typical_loading_rate": 8000},
        {"name": "Chemicals", "category": "liquid_bulk", "handling_complexity": 1.8, "requires_special_equipment": True, "is_hazardous": True, "typical_loading_rate": 3000},
        {"name": "Steel Products", "category": "break_bulk", "handling_complexity": 1.5, "requires_special_equipment": True, "is_hazardous": False, "typical_loading_rate": 2000},
        {"name": "Bauxite", "category": "dry_bulk", "handling_complexity": 0.85, "requires_special_equipment": False, "is_hazardous": False, "typical_loading_rate": 7000},
    ]
    
    cargo_types = []
    for ct_data in cargo_types_data:
        cargo_type = CargoType(**ct_data)
        db.session.add(cargo_type)
        cargo_types.append(cargo_type)
    
    db.session.flush()
    
    delay_causes = [
        ("Port Congestion", "congestion"),
        ("Berth Unavailable", "berth"),
        ("Weather Delay", "weather"),
        ("Cargo Operations Delay", "operations"),
        ("Documentation Issues", "documentation"),
        ("Draft Restrictions", "draft"),
        ("Equipment Breakdown", "equipment"),
    ]
    
    for i in range(30):
        vessel = random.choice(vessels)
        origin = random.choice(ports)
        dest = random.choice([p for p in ports if p != origin])
        cargo = random.choice(cargo_types)
        
        days_ago = random.randint(1, 180)
        eta = datetime.utcnow() - timedelta(days=days_ago)
        delay = random.uniform(2, 72)
        
        voyage = Voyage(
            vessel_id=vessel.id,
            origin_port_id=origin.id,
            destination_port_id=dest.id,
            cargo_type_id=cargo.id,
            cargo_volume=random.uniform(10000, 150000),
            eta=eta,
            ata=eta + timedelta(hours=random.uniform(-2, 6)),
            berthing_time=eta + timedelta(hours=delay),
            departure_time=eta + timedelta(hours=delay + random.uniform(24, 96)),
            predicted_delay_hours=delay * random.uniform(0.7, 1.3),
            predicted_demurrage_cost=(delay / 24) * vessel.demurrage_rate * random.uniform(0.7, 1.3),
            actual_delay_hours=delay,
            actual_demurrage_cost=(delay / 24) * vessel.demurrage_rate,
            status="completed",
            created_at=eta - timedelta(days=random.randint(7, 30))
        )
        db.session.add(voyage)
        db.session.flush()
        
        cause, category = random.choice(delay_causes)
        demurrage_record = DemurrageRecord(
            voyage_id=voyage.id,
            delay_hours=delay,
            cost=(delay / 24) * vessel.demurrage_rate,
            cause=cause,
            cause_category=category,
            recorded_at=voyage.departure_time,
            notes=f"Delay at {dest.name} due to {cause.lower()}"
        )
        db.session.add(demurrage_record)
    
    db.session.commit()
    print("Database seeded with sample maritime data.")

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
