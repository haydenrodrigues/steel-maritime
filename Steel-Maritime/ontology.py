class MaritimeOntology:
    def __init__(self):
        self._build_ontology()
    
    def _build_ontology(self):
        self.vessel_types = {
            "bulk_carrier": {
                "name": "Bulk Carrier",
                "category": "dry_bulk",
                "subtypes": ["Handysize", "Handymax", "Supramax", "Panamax", "Capesize", "VLOC"],
                "compatible_cargo": ["iron_ore", "coal", "grain", "bauxite", "phosphate", "cement"],
                "loading_characteristics": {
                    "typical_rate_factor": 1.0,
                    "weather_sensitivity": "moderate",
                    "port_infrastructure_needs": "moderate"
                }
            },
            "tanker": {
                "name": "Tanker",
                "category": "liquid",
                "subtypes": ["Product Tanker", "Aframax", "Suezmax", "VLCC", "ULCC"],
                "compatible_cargo": ["crude_oil", "refined_products", "chemicals", "lng", "lpg"],
                "loading_characteristics": {
                    "typical_rate_factor": 1.2,
                    "weather_sensitivity": "low",
                    "port_infrastructure_needs": "high"
                }
            },
            "container": {
                "name": "Container Ship",
                "category": "containerized",
                "subtypes": ["Feeder", "Panamax", "Post-Panamax", "New Panamax", "Ultra Large"],
                "compatible_cargo": ["container", "reefer_container", "special_container"],
                "loading_characteristics": {
                    "typical_rate_factor": 0.8,
                    "weather_sensitivity": "moderate",
                    "port_infrastructure_needs": "very_high"
                }
            },
            "general_cargo": {
                "name": "General Cargo",
                "category": "break_bulk",
                "subtypes": ["Multipurpose", "Heavy Lift", "Ro-Ro"],
                "compatible_cargo": ["project_cargo", "steel", "machinery", "vehicles", "general"],
                "loading_characteristics": {
                    "typical_rate_factor": 0.6,
                    "weather_sensitivity": "high",
                    "port_infrastructure_needs": "moderate"
                }
            }
        }
        
        self.cargo_types = {
            "iron_ore": {
                "name": "Iron Ore",
                "category": "dry_bulk",
                "handling_complexity": 0.8,
                "typical_loading_rate": 8000,
                "hazardous": False,
                "weather_sensitive": False,
                "special_requirements": []
            },
            "coal": {
                "name": "Coal",
                "category": "dry_bulk",
                "handling_complexity": 0.9,
                "typical_loading_rate": 6000,
                "hazardous": False,
                "weather_sensitive": True,
                "special_requirements": ["dust_control"]
            },
            "grain": {
                "name": "Grain",
                "category": "dry_bulk",
                "handling_complexity": 1.0,
                "typical_loading_rate": 5000,
                "hazardous": False,
                "weather_sensitive": True,
                "special_requirements": ["fumigation", "moisture_control"]
            },
            "crude_oil": {
                "name": "Crude Oil",
                "category": "liquid_bulk",
                "handling_complexity": 1.2,
                "typical_loading_rate": 10000,
                "hazardous": True,
                "weather_sensitive": False,
                "special_requirements": ["vapor_recovery", "inert_gas"]
            },
            "container": {
                "name": "Containers",
                "category": "containerized",
                "handling_complexity": 0.7,
                "typical_loading_rate": 30,
                "hazardous": False,
                "weather_sensitive": False,
                "special_requirements": ["crane_access"]
            },
            "lng": {
                "name": "LNG",
                "category": "liquid_bulk",
                "handling_complexity": 2.0,
                "typical_loading_rate": 8000,
                "hazardous": True,
                "weather_sensitive": False,
                "special_requirements": ["cryogenic_handling", "specialized_terminal"]
            },
            "chemicals": {
                "name": "Chemicals",
                "category": "liquid_bulk",
                "handling_complexity": 1.8,
                "typical_loading_rate": 3000,
                "hazardous": True,
                "weather_sensitive": False,
                "special_requirements": ["tank_coating", "segregation"]
            },
            "project_cargo": {
                "name": "Project Cargo",
                "category": "break_bulk",
                "handling_complexity": 2.5,
                "typical_loading_rate": 500,
                "hazardous": False,
                "weather_sensitive": True,
                "special_requirements": ["heavy_lift", "special_stowage"]
            }
        }
        
        self.port_capabilities = {
            "bulk_terminal": {
                "name": "Bulk Terminal",
                "handles": ["iron_ore", "coal", "grain", "bauxite", "phosphate"],
                "equipment": ["grab_cranes", "conveyor_systems", "ship_loaders"],
                "efficiency_factors": {
                    "modern": 1.2,
                    "standard": 1.0,
                    "basic": 0.7
                }
            },
            "oil_terminal": {
                "name": "Oil Terminal",
                "handles": ["crude_oil", "refined_products"],
                "equipment": ["loading_arms", "manifolds", "vapor_recovery"],
                "efficiency_factors": {
                    "deep_water": 1.3,
                    "standard": 1.0,
                    "shallow": 0.6
                }
            },
            "container_terminal": {
                "name": "Container Terminal",
                "handles": ["container", "reefer_container"],
                "equipment": ["gantry_cranes", "rtg", "reach_stackers"],
                "efficiency_factors": {
                    "automated": 1.4,
                    "semi_automated": 1.2,
                    "manual": 0.8
                }
            },
            "lng_terminal": {
                "name": "LNG Terminal",
                "handles": ["lng"],
                "equipment": ["cryogenic_arms", "boil_off_gas_system"],
                "efficiency_factors": {
                    "modern": 1.1,
                    "standard": 1.0
                }
            },
            "multipurpose": {
                "name": "Multipurpose Terminal",
                "handles": ["general", "project_cargo", "steel", "vehicles"],
                "equipment": ["mobile_cranes", "forklifts", "ramps"],
                "efficiency_factors": {
                    "well_equipped": 1.1,
                    "standard": 1.0,
                    "basic": 0.8
                }
            }
        }
        
        self.delay_causes = {
            "port_congestion": {
                "name": "Port Congestion",
                "typical_delay_range": (6, 72),
                "mitigation": ["early_arrival", "alternative_port", "scheduling_optimization"],
                "predictability": "moderate"
            },
            "berth_unavailability": {
                "name": "Berth Unavailability",
                "typical_delay_range": (4, 48),
                "mitigation": ["berth_booking", "flexible_scheduling", "priority_arrangements"],
                "predictability": "high"
            },
            "weather": {
                "name": "Weather Delays",
                "typical_delay_range": (2, 96),
                "mitigation": ["seasonal_planning", "weather_routing", "buffer_time"],
                "predictability": "moderate"
            },
            "cargo_operations": {
                "name": "Cargo Handling Delays",
                "typical_delay_range": (2, 24),
                "mitigation": ["equipment_coordination", "shift_optimization", "stevedore_efficiency"],
                "predictability": "high"
            },
            "documentation": {
                "name": "Documentation Issues",
                "typical_delay_range": (1, 12),
                "mitigation": ["pre_clearance", "digital_documentation", "agent_coordination"],
                "predictability": "high"
            },
            "draft_restrictions": {
                "name": "Draft/Tide Restrictions",
                "typical_delay_range": (2, 24),
                "mitigation": ["tide_scheduling", "lightening", "alternative_berth"],
                "predictability": "very_high"
            },
            "equipment_failure": {
                "name": "Equipment Breakdown",
                "typical_delay_range": (4, 48),
                "mitigation": ["backup_equipment", "maintenance_scheduling", "alternative_methods"],
                "predictability": "low"
            }
        }
        
        self.demurrage_factors = {
            "vessel_size": {
                "handysize": 0.7,
                "handymax": 0.85,
                "panamax": 1.0,
                "capesize": 1.3,
                "vlcc": 1.5
            },
            "cargo_complexity": {
                "simple": 0.8,
                "standard": 1.0,
                "complex": 1.3,
                "specialized": 1.6
            },
            "port_efficiency": {
                "very_high": 0.7,
                "high": 0.85,
                "moderate": 1.0,
                "low": 1.3,
                "very_low": 1.6
            },
            "seasonal": {
                "peak": 1.3,
                "normal": 1.0,
                "low": 0.85
            }
        }
    
    def get_vessel_types(self):
        return self.vessel_types
    
    def get_cargo_types(self):
        return self.cargo_types
    
    def get_port_capabilities(self):
        return self.port_capabilities
    
    def get_delay_causes(self):
        return self.delay_causes
    
    def get_cargo_relationships(self):
        relationships = []
        for vessel_key, vessel_data in self.vessel_types.items():
            for cargo in vessel_data["compatible_cargo"]:
                if cargo in self.cargo_types:
                    relationships.append({
                        "vessel_type": vessel_data["name"],
                        "cargo_type": self.cargo_types[cargo]["name"],
                        "compatibility": "high"
                    })
        return relationships
    
    def get_compatibility_score(self, vessel_type_key, cargo_type_key):
        if vessel_type_key not in self.vessel_types:
            return 0.5
        
        vessel = self.vessel_types[vessel_type_key]
        if cargo_type_key in vessel["compatible_cargo"]:
            return 1.0
        return 0.3
    
    def get_port_efficiency_for_cargo(self, port_capability_key, cargo_type_key):
        if port_capability_key not in self.port_capabilities:
            return 0.5
        
        capability = self.port_capabilities[port_capability_key]
        if cargo_type_key in capability["handles"]:
            return 1.0
        return 0.4
    
    def get_handling_complexity(self, cargo_type_key):
        if cargo_type_key in self.cargo_types:
            return self.cargo_types[cargo_type_key]["handling_complexity"]
        return 1.0
    
    def get_demurrage_risk_factors(self, vessel_size_category, cargo_complexity, port_efficiency, season="normal"):
        factors = {
            "vessel_factor": self.demurrage_factors["vessel_size"].get(vessel_size_category, 1.0),
            "cargo_factor": self.demurrage_factors["cargo_complexity"].get(cargo_complexity, 1.0),
            "port_factor": self.demurrage_factors["port_efficiency"].get(port_efficiency, 1.0),
            "seasonal_factor": self.demurrage_factors["seasonal"].get(season, 1.0)
        }
        factors["combined_risk"] = (
            factors["vessel_factor"] * 
            factors["cargo_factor"] * 
            factors["port_factor"] * 
            factors["seasonal_factor"]
        )
        return factors
