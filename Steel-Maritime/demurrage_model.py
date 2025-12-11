import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import random

class DemurragePredictor:
    def __init__(self):
        self.base_delay_hours = 8
        self.congestion_weight = 0.3
        self.cargo_complexity_weight = 0.2
        self.weather_weight = 0.15
        self.port_efficiency_weight = 0.2
        self.vessel_compatibility_weight = 0.15
    
    def predict_demurrage(self, vessel, origin_port, dest_port, cargo_type, cargo_volume, eta, ontology):
        if not all([vessel, dest_port]):
            return self._empty_prediction()
        
        port_congestion_score = self._calculate_congestion_score(dest_port, eta)
        
        cargo_handling_score = self._calculate_cargo_handling_score(cargo_type, cargo_volume, ontology)
        
        weather_score = self._calculate_weather_score(dest_port, eta)
        
        port_efficiency_score = self._calculate_port_efficiency_score(dest_port, cargo_type, ontology)
        
        vessel_compatibility_score = self._calculate_vessel_compatibility(vessel, cargo_type, ontology)
        
        combined_delay_factor = (
            self.congestion_weight * port_congestion_score +
            self.cargo_complexity_weight * cargo_handling_score +
            self.weather_weight * weather_score +
            self.port_efficiency_weight * (1 - port_efficiency_score) +
            self.vessel_compatibility_weight * (1 - vessel_compatibility_score)
        )
        
        predicted_delay_hours = self.base_delay_hours * (1 + combined_delay_factor * 3)
        
        delay_std = predicted_delay_hours * 0.3
        confidence_interval = stats.norm.interval(0.95, loc=predicted_delay_hours, scale=delay_std)
        
        daily_rate = vessel.demurrage_rate if vessel.demurrage_rate else 25000
        predicted_cost = (predicted_delay_hours / 24) * daily_rate
        
        risk_level = self._calculate_risk_level(combined_delay_factor)
        
        loading_time = self._estimate_loading_time(cargo_volume, cargo_type, dest_port, ontology)
        
        recommendations = self._generate_recommendations(
            port_congestion_score, cargo_handling_score, weather_score,
            port_efficiency_score, vessel_compatibility_score, eta, dest_port
        )
        
        return {
            "predicted_delay_hours": round(predicted_delay_hours, 1),
            "delay_range": {
                "min": round(max(0, confidence_interval[0]), 1),
                "max": round(confidence_interval[1], 1)
            },
            "predicted_cost": round(predicted_cost, 2),
            "cost_range": {
                "min": round((max(0, confidence_interval[0]) / 24) * daily_rate, 2),
                "max": round((confidence_interval[1] / 24) * daily_rate, 2)
            },
            "risk_level": risk_level,
            "risk_factors": {
                "port_congestion": round(port_congestion_score * 100, 1),
                "cargo_handling": round(cargo_handling_score * 100, 1),
                "weather": round(weather_score * 100, 1),
                "port_efficiency": round((1 - port_efficiency_score) * 100, 1),
                "vessel_compatibility": round((1 - vessel_compatibility_score) * 100, 1)
            },
            "estimated_loading_time_hours": round(loading_time, 1),
            "recommendations": recommendations,
            "optimal_arrival_window": self._calculate_optimal_arrival(eta, dest_port),
            "potential_savings": round(predicted_cost * 0.3, 2)
        }
    
    def _empty_prediction(self):
        return {
            "predicted_delay_hours": 0,
            "delay_range": {"min": 0, "max": 0},
            "predicted_cost": 0,
            "cost_range": {"min": 0, "max": 0},
            "risk_level": "unknown",
            "risk_factors": {},
            "estimated_loading_time_hours": 0,
            "recommendations": [],
            "optimal_arrival_window": None,
            "potential_savings": 0
        }
    
    def _calculate_congestion_score(self, port, eta):
        base_congestion = port.avg_congestion_level if port.avg_congestion_level else 0.5
        
        if eta:
            day_of_week = eta.weekday()
            hour = eta.hour
            
            if day_of_week < 5:
                base_congestion *= 1.1
            
            if 8 <= hour <= 18:
                base_congestion *= 1.15
            else:
                base_congestion *= 0.9
            
            month = eta.month
            if month in [3, 4, 9, 10]:
                base_congestion *= 1.2
        
        return min(1.0, base_congestion)
    
    def _calculate_cargo_handling_score(self, cargo_type, cargo_volume, ontology):
        if not cargo_type:
            return 0.5
        
        complexity = cargo_type.handling_complexity if cargo_type.handling_complexity else 1.0
        
        volume_factor = 1.0
        if cargo_volume > 50000:
            volume_factor = 1.3
        elif cargo_volume > 20000:
            volume_factor = 1.1
        
        if cargo_type.requires_special_equipment:
            complexity *= 1.2
        
        if cargo_type.is_hazardous:
            complexity *= 1.3
        
        return min(1.0, (complexity * volume_factor - 0.5) / 2)
    
    def _calculate_weather_score(self, port, eta):
        base_weather = port.weather_delay_factor if port.weather_delay_factor else 1.0
        
        if eta:
            month = eta.month
            if month in [12, 1, 2]:
                base_weather *= 1.4
            elif month in [6, 7, 8]:
                base_weather *= 0.8
        
        lat = port.latitude if port.latitude else 0
        if abs(lat) > 45:
            base_weather *= 1.2
        
        return min(1.0, (base_weather - 0.5) / 1.5)
    
    def _calculate_port_efficiency_score(self, port, cargo_type, ontology):
        if not port:
            return 0.5
        
        base_efficiency = 0.7
        
        if port.cargo_handling_rate:
            if port.cargo_handling_rate > 8000:
                base_efficiency = 0.9
            elif port.cargo_handling_rate > 5000:
                base_efficiency = 0.75
            else:
                base_efficiency = 0.6
        
        if port.num_berths:
            if port.num_berths > 10:
                base_efficiency *= 1.1
            elif port.num_berths < 3:
                base_efficiency *= 0.85
        
        return min(1.0, base_efficiency)
    
    def _calculate_vessel_compatibility(self, vessel, cargo_type, ontology):
        if not vessel or not cargo_type:
            return 0.7
        
        if vessel.vessel_type:
            vessel_type_name = vessel.vessel_type.name.lower()
            cargo_category = cargo_type.category.lower() if cargo_type.category else ""
            
            compatibility_matrix = {
                "bulk carrier": ["dry_bulk", "dry bulk"],
                "tanker": ["liquid_bulk", "liquid bulk", "liquid"],
                "container": ["containerized", "container"],
                "general cargo": ["break_bulk", "break bulk", "general"]
            }
            
            for v_type, compatible_cargos in compatibility_matrix.items():
                if v_type in vessel_type_name:
                    if any(c in cargo_category for c in compatible_cargos):
                        return 1.0
                    return 0.5
        
        return 0.7
    
    def _calculate_risk_level(self, combined_factor):
        if combined_factor < 0.3:
            return "low"
        elif combined_factor < 0.5:
            return "moderate"
        elif combined_factor < 0.7:
            return "high"
        else:
            return "critical"
    
    def _estimate_loading_time(self, cargo_volume, cargo_type, port, ontology):
        if not cargo_volume or cargo_volume <= 0:
            return 0
        
        base_rate = 5000
        
        if port and port.cargo_handling_rate:
            base_rate = port.cargo_handling_rate
        elif cargo_type and cargo_type.typical_loading_rate:
            base_rate = cargo_type.typical_loading_rate
        
        loading_hours = cargo_volume / base_rate
        
        if cargo_type and cargo_type.handling_complexity:
            loading_hours *= cargo_type.handling_complexity
        
        return loading_hours
    
    def _generate_recommendations(self, congestion, cargo, weather, port_eff, vessel_compat, eta, port):
        recommendations = []
        
        if congestion > 0.6:
            recommendations.append({
                "priority": "high",
                "category": "scheduling",
                "action": "Consider arriving 24-48 hours earlier to secure berth slot",
                "potential_saving": "15-25%"
            })
            recommendations.append({
                "priority": "medium",
                "category": "communication",
                "action": "Contact port agent to pre-book berth window",
                "potential_saving": "10-15%"
            })
        
        if cargo > 0.5:
            recommendations.append({
                "priority": "high",
                "category": "operations",
                "action": "Pre-arrange specialized equipment and stevedores",
                "potential_saving": "10-20%"
            })
        
        if weather > 0.5:
            recommendations.append({
                "priority": "medium",
                "category": "planning",
                "action": "Build weather buffer into schedule",
                "potential_saving": "5-15%"
            })
        
        if port_eff > 0.4:
            recommendations.append({
                "priority": "medium",
                "category": "alternatives",
                "action": "Evaluate nearby alternative ports with better efficiency",
                "potential_saving": "10-30%"
            })
        
        if vessel_compat < 0.7:
            recommendations.append({
                "priority": "low",
                "category": "fleet",
                "action": "Consider using more suitable vessel type for this cargo",
                "potential_saving": "5-10%"
            })
        
        recommendations.append({
            "priority": "medium",
            "category": "documentation",
            "action": "Submit all documentation 48 hours before arrival",
            "potential_saving": "5-10%"
        })
        
        return sorted(recommendations, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])
    
    def _calculate_optimal_arrival(self, eta, port):
        if not eta:
            return None
        
        best_hour = 6
        current_hour = eta.hour
        
        adjustment = best_hour - current_hour
        optimal_time = eta + timedelta(hours=adjustment)
        
        if optimal_time.weekday() >= 5:
            days_to_monday = 7 - optimal_time.weekday()
            optimal_time += timedelta(days=days_to_monday)
        
        return {
            "start": optimal_time.strftime("%Y-%m-%d %H:%M"),
            "end": (optimal_time + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
            "reason": "Lower congestion during early morning weekday arrivals"
        }
    
    def get_optimization_recommendations(self, vessel, dest_port, cargo_type, cargo_volume, ontology):
        base_prediction = self.predict_demurrage(
            vessel=vessel,
            origin_port=None,
            dest_port=dest_port,
            cargo_type=cargo_type,
            cargo_volume=cargo_volume,
            eta=datetime.utcnow() + timedelta(days=7),
            ontology=ontology
        )
        
        time_slots = []
        for day_offset in range(14):
            for hour in [6, 12, 18]:
                test_eta = datetime.utcnow() + timedelta(days=day_offset, hours=hour)
                prediction = self.predict_demurrage(
                    vessel=vessel,
                    origin_port=None,
                    dest_port=dest_port,
                    cargo_type=cargo_type,
                    cargo_volume=cargo_volume,
                    eta=test_eta,
                    ontology=ontology
                )
                time_slots.append({
                    "eta": test_eta.strftime("%Y-%m-%d %H:%M"),
                    "predicted_cost": prediction["predicted_cost"],
                    "risk_level": prediction["risk_level"]
                })
        
        time_slots.sort(key=lambda x: x["predicted_cost"])
        
        return {
            "current_prediction": base_prediction,
            "best_arrival_times": time_slots[:5],
            "worst_arrival_times": time_slots[-3:],
            "potential_maximum_savings": round(time_slots[-1]["predicted_cost"] - time_slots[0]["predicted_cost"], 2)
        }
