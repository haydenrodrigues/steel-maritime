from datetime import datetime

def init_models(db):
    
    class VesselType(db.Model):
        __tablename__ = "vessel_types"
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        category = db.Column(db.String(50))
        typical_dwt_min = db.Column(db.Float)
        typical_dwt_max = db.Column(db.Float)
        loading_rate_factor = db.Column(db.Float, default=1.0)
        
        vessels = db.relationship("Vessel", backref="vessel_type", lazy=True)

    class Vessel(db.Model):
        __tablename__ = "vessels"
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False)
        imo_number = db.Column(db.String(20), unique=True)
        vessel_type_id = db.Column(db.Integer, db.ForeignKey("vessel_types.id"))
        dwt = db.Column(db.Float)
        loa = db.Column(db.Float)
        beam = db.Column(db.Float)
        draft = db.Column(db.Float)
        demurrage_rate = db.Column(db.Float, default=25000)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        voyages = db.relationship("Voyage", backref="vessel", lazy=True)

    class Port(db.Model):
        __tablename__ = "ports"
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(200), nullable=False)
        code = db.Column(db.String(10))
        country = db.Column(db.String(100))
        latitude = db.Column(db.Float)
        longitude = db.Column(db.Float)
        avg_congestion_level = db.Column(db.Float, default=0.5)
        avg_berth_wait_hours = db.Column(db.Float, default=12)
        num_berths = db.Column(db.Integer, default=5)
        max_draft = db.Column(db.Float, default=15.0)
        cargo_handling_rate = db.Column(db.Float, default=5000)
        weather_delay_factor = db.Column(db.Float, default=1.0)
        
        origin_voyages = db.relationship("Voyage", backref="origin_port", 
                                         foreign_keys="Voyage.origin_port_id", lazy=True)
        destination_voyages = db.relationship("Voyage", backref="destination_port",
                                              foreign_keys="Voyage.destination_port_id", lazy=True)

    class CargoType(db.Model):
        __tablename__ = "cargo_types"
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        category = db.Column(db.String(50))
        handling_complexity = db.Column(db.Float, default=1.0)
        requires_special_equipment = db.Column(db.Boolean, default=False)
        is_hazardous = db.Column(db.Boolean, default=False)
        typical_loading_rate = db.Column(db.Float)
        
        voyages = db.relationship("Voyage", backref="cargo_type", lazy=True)

    class Voyage(db.Model):
        __tablename__ = "voyages"
        
        id = db.Column(db.Integer, primary_key=True)
        vessel_id = db.Column(db.Integer, db.ForeignKey("vessels.id"), nullable=False)
        origin_port_id = db.Column(db.Integer, db.ForeignKey("ports.id"))
        destination_port_id = db.Column(db.Integer, db.ForeignKey("ports.id"), nullable=False)
        cargo_type_id = db.Column(db.Integer, db.ForeignKey("cargo_types.id"))
        cargo_volume = db.Column(db.Float)
        eta = db.Column(db.DateTime)
        ata = db.Column(db.DateTime)
        berthing_time = db.Column(db.DateTime)
        departure_time = db.Column(db.DateTime)
        predicted_delay_hours = db.Column(db.Float)
        predicted_demurrage_cost = db.Column(db.Float)
        actual_delay_hours = db.Column(db.Float)
        actual_demurrage_cost = db.Column(db.Float)
        status = db.Column(db.String(50), default="planned")
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        demurrage_records = db.relationship("DemurrageRecord", backref="voyage", lazy=True)

    class DemurrageRecord(db.Model):
        __tablename__ = "demurrage_records"
        
        id = db.Column(db.Integer, primary_key=True)
        voyage_id = db.Column(db.Integer, db.ForeignKey("voyages.id"), nullable=False)
        delay_hours = db.Column(db.Float, nullable=False)
        cost = db.Column(db.Float, nullable=False)
        cause = db.Column(db.String(200))
        cause_category = db.Column(db.String(50))
        recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
        notes = db.Column(db.Text)

    class PortCapability(db.Model):
        __tablename__ = "port_capabilities"
        
        id = db.Column(db.Integer, primary_key=True)
        port_id = db.Column(db.Integer, db.ForeignKey("ports.id"), nullable=False)
        cargo_type_id = db.Column(db.Integer, db.ForeignKey("cargo_types.id"), nullable=False)
        efficiency_rating = db.Column(db.Float, default=1.0)
        has_specialized_equipment = db.Column(db.Boolean, default=True)
        
        port = db.relationship("Port", backref="capabilities")
        cargo_type = db.relationship("CargoType", backref="port_capabilities")

    class VesselCargoCompatibility(db.Model):
        __tablename__ = "vessel_cargo_compatibility"
        
        id = db.Column(db.Integer, primary_key=True)
        vessel_type_id = db.Column(db.Integer, db.ForeignKey("vessel_types.id"), nullable=False)
        cargo_type_id = db.Column(db.Integer, db.ForeignKey("cargo_types.id"), nullable=False)
        compatibility_score = db.Column(db.Float, default=1.0)
        
        vessel_type = db.relationship("VesselType", backref="cargo_compatibilities")
        cargo_type = db.relationship("CargoType", backref="vessel_compatibilities")
    
    return {
        'VesselType': VesselType,
        'Vessel': Vessel,
        'Port': Port,
        'CargoType': CargoType,
        'Voyage': Voyage,
        'DemurrageRecord': DemurrageRecord,
        'PortCapability': PortCapability,
        'VesselCargoCompatibility': VesselCargoCompatibility
    }
