"""Dashboard and visualization components for Genetic Load Manager."""
import logging
import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)
from .const import DOMAIN

class OptimizationDashboardSensor(SensorEntity):
    """Dashboard sensor providing comprehensive optimization metrics."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the dashboard sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_optimization_dashboard"
        self._attr_name = "Genetic Load Manager Dashboard"
        self._attr_unit_of_measurement = PERCENTAGE
        self._attr_device_class = "battery"
        self._attr_state_class = "measurement"
        self._state = None
        
        # Dashboard data
        self._dashboard_data = {
            "current_status": "idle",
            "optimization_progress": 0,
            "cost_savings": {"daily": 0, "weekly": 0, "monthly": 0},
            "efficiency_metrics": {"solar_utilization": 0, "load_optimization": 0},
            "system_health": {"status": "unknown", "issues": []},
            "recent_optimizations": [],
            "schedule_preview": [],
            "performance_trends": []
        }
        
        # Performance tracking
        self._performance_history = []
        self._cost_history = []
        self._optimization_history = []

    @property
    def state(self):
        """Return the optimization progress percentage."""
        return self._dashboard_data["optimization_progress"]

    @property
    def extra_state_attributes(self):
        """Return comprehensive dashboard data as attributes."""
        return {
            "dashboard_data": self._dashboard_data,
            "last_updated": datetime.now().isoformat(),
            "visualization_ready": True,
            "chart_data": self._generate_chart_data(),
            "quick_stats": self._generate_quick_stats()
        }

    async def async_added_to_hass(self):
        """Set up periodic updates for the dashboard."""
        async_track_time_interval(self.hass, self.async_update, timedelta(minutes=1))
        await self.async_update()

    async def async_update(self):
        """Update dashboard with latest data."""
        try:
            # Get genetic algorithm instance
            genetic_algo = self.hass.data.get(DOMAIN, {}).get('genetic_algorithm')
            
            if genetic_algo:
                await self._update_optimization_status(genetic_algo)
                await self._update_cost_savings()
                await self._update_efficiency_metrics(genetic_algo)
                await self._update_system_health(genetic_algo)
                await self._update_schedule_preview(genetic_algo)
                await self._update_performance_trends()
            
            # Update state (overall system health percentage)
            self._state = self._calculate_overall_health()
            
        except Exception as e:
            _LOGGER.error(f"Error updating dashboard: {e}")

    async def _update_optimization_status(self, genetic_algo):
        """Update current optimization status."""
        try:
            if hasattr(genetic_algo, 'is_running') and genetic_algo.is_running:
                # Check if optimization is currently running
                status_sensor = self.hass.states.get("sensor.genetic_algorithm_status")
                if status_sensor and status_sensor.state == "running":
                    self._dashboard_data["current_status"] = "optimizing"
                    generation = status_sensor.attributes.get("generation", 0)
                    max_generations = getattr(genetic_algo, 'generations', 100)
                    self._dashboard_data["optimization_progress"] = min(100, (generation / max_generations) * 100)
                else:
                    self._dashboard_data["current_status"] = "active"
                    self._dashboard_data["optimization_progress"] = 100
            else:
                self._dashboard_data["current_status"] = "idle"
                self._dashboard_data["optimization_progress"] = 0
        except Exception as e:
            _LOGGER.error(f"Error updating optimization status: {e}")
            self._dashboard_data["current_status"] = "error"

    async def _update_cost_savings(self):
        """Calculate and update cost savings metrics."""
        try:
            # Get pricing sensor data
            pricing_sensor = self.hass.states.get(f"sensor.{DOMAIN}_indexed_pricing")
            if pricing_sensor:
                current_price = float(pricing_sensor.state or 0)
                
                # Simulate cost savings calculation (in real implementation, compare with baseline)
                daily_consumption = 25  # kWh estimate
                baseline_cost = daily_consumption * current_price * 1.2  # 20% higher without optimization
                optimized_cost = daily_consumption * current_price
                daily_savings = baseline_cost - optimized_cost
                
                self._dashboard_data["cost_savings"] = {
                    "daily": round(daily_savings, 2),
                    "weekly": round(daily_savings * 7, 2),
                    "monthly": round(daily_savings * 30, 2)
                }
                
                # Store for trend analysis
                self._cost_history.append({
                    "timestamp": datetime.now(),
                    "savings": daily_savings,
                    "price": current_price
                })
                
                # Keep only last 30 days
                cutoff = datetime.now() - timedelta(days=30)
                self._cost_history = [h for h in self._cost_history if h["timestamp"] > cutoff]
                
        except Exception as e:
            _LOGGER.error(f"Error updating cost savings: {e}")

    async def _update_efficiency_metrics(self, genetic_algo):
        """Update system efficiency metrics."""
        try:
            # Solar utilization
            if hasattr(genetic_algo, 'pv_forecast') and genetic_algo.pv_forecast is not None:
                total_solar = sum(genetic_algo.pv_forecast)
                if total_solar > 0:
                    # Estimate utilization (in real implementation, compare with actual usage)
                    utilization = min(100, (total_solar * 0.85) / total_solar * 100)  # 85% utilization estimate
                    self._dashboard_data["efficiency_metrics"]["solar_utilization"] = round(utilization, 1)
            
            # Load optimization efficiency
            if hasattr(genetic_algo, 'population') and genetic_algo.population is not None:
                # Estimate load optimization based on fitness improvement
                self._dashboard_data["efficiency_metrics"]["load_optimization"] = 78.5  # Example value
            
        except Exception as e:
            _LOGGER.error(f"Error updating efficiency metrics: {e}")

    async def _update_system_health(self, genetic_algo):
        """Update system health status."""
        try:
            issues = []
            status = "healthy"
            
            # Check genetic algorithm health
            if not hasattr(genetic_algo, 'is_running') or not genetic_algo.is_running:
                issues.append("Genetic algorithm not running")
                status = "warning"
            
            # Check pricing data availability
            pricing_sensor = self.hass.states.get(f"sensor.{DOMAIN}_indexed_pricing")
            if not pricing_sensor or pricing_sensor.state in ['unknown', 'unavailable']:
                issues.append("Pricing data unavailable")
                status = "warning"
            
            # Check forecast data
            if not hasattr(genetic_algo, 'pv_forecast') or genetic_algo.pv_forecast is None:
                issues.append("Solar forecast unavailable")
                status = "warning"
            
            if len(issues) > 2:
                status = "error"
            
            self._dashboard_data["system_health"] = {
                "status": status,
                "issues": issues,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            _LOGGER.error(f"Error updating system health: {e}")
            self._dashboard_data["system_health"] = {
                "status": "error",
                "issues": [f"Health check failed: {str(e)}"],
                "last_check": datetime.now().isoformat()
            }

    async def _update_schedule_preview(self, genetic_algo):
        """Update upcoming schedule preview."""
        try:
            schedule_preview = []
            current_time = datetime.now()
            
            # Generate next 8 hours of schedule preview
            for i in range(8):
                hour_time = current_time + timedelta(hours=i)
                
                # Get pricing for this hour
                pricing_sensor = self.hass.states.get(f"sensor.{DOMAIN}_indexed_pricing")
                if pricing_sensor and 'forecast' in pricing_sensor.attributes:
                    forecast = pricing_sensor.attributes['forecast']
                    price = forecast[i] if i < len(forecast) else 0.1
                else:
                    price = 0.1
                
                # Simulate device schedule (in real implementation, get from genetic algorithm)
                device_status = "on" if price < 0.15 else "off"  # Simple rule for demo
                
                schedule_preview.append({
                    "time": hour_time.strftime("%H:%M"),
                    "price": round(price, 4),
                    "devices": {
                        "device_0": device_status,
                                              "device_1": "on" if price < 0.12 else "off"
                  },
                  "solar_forecast": round(random.uniform(0, 2), 2),  # Demo data
                  "load_forecast": round(random.uniform(0.5, 1.5), 2)  # Demo data
                })
            
            self._dashboard_data["schedule_preview"] = schedule_preview
            
        except Exception as e:
            _LOGGER.error(f"Error updating schedule preview: {e}")

    async def _update_performance_trends(self):
        """Update performance trend data."""
        try:
            # Add current performance data point
            current_performance = {
                "timestamp": datetime.now(),
                "optimization_score": self._dashboard_data["optimization_progress"],
                "cost_savings": self._dashboard_data["cost_savings"]["daily"],
                "solar_utilization": self._dashboard_data["efficiency_metrics"]["solar_utilization"],
                "system_health_score": self._calculate_overall_health()
            }
            
            self._performance_history.append(current_performance)
            
            # Keep only last 7 days
            cutoff = datetime.now() - timedelta(days=7)
            self._performance_history = [h for h in self._performance_history if h["timestamp"] > cutoff]
            
            # Generate trend data for charts
            self._dashboard_data["performance_trends"] = [
                {
                    "time": p["timestamp"].strftime("%Y-%m-%d %H:%M"),
                    "optimization": p["optimization_score"],
                    "savings": p["cost_savings"],
                    "solar": p["solar_utilization"],
                    "health": p["system_health_score"]
                }
                for p in self._performance_history[-24:]  # Last 24 data points
            ]
            
        except Exception as e:
            _LOGGER.error(f"Error updating performance trends: {e}")

    def _generate_chart_data(self):
        """Generate data formatted for charts."""
        try:
            return {
                "cost_savings_chart": {
                    "labels": [h["timestamp"].strftime("%H:%M") for h in self._cost_history[-12:]],
                    "data": [h["savings"] for h in self._cost_history[-12:]],
                    "type": "line"
                },
                "efficiency_pie": {
                    "labels": ["Solar Utilization", "Grid Usage"],
                    "data": [
                        self._dashboard_data["efficiency_metrics"]["solar_utilization"],
                        100 - self._dashboard_data["efficiency_metrics"]["solar_utilization"]
                    ],
                    "type": "pie"
                },
                "schedule_bar": {
                    "labels": [s["time"] for s in self._dashboard_data["schedule_preview"]],
                    "datasets": [
                        {
                            "label": "Price (€/kWh)",
                            "data": [s["price"] for s in self._dashboard_data["schedule_preview"]],
                            "type": "bar"
                        }
                    ]
                }
            }
        except Exception as e:
            _LOGGER.error(f"Error generating chart data: {e}")
            return {}

    def _generate_quick_stats(self):
        """Generate quick statistics for dashboard."""
        try:
            return {
                "total_devices": len([s for s in self._dashboard_data["schedule_preview"] if s.get("devices")]),
                "active_optimizations": 1 if self._dashboard_data["current_status"] == "optimizing" else 0,
                "daily_cost_savings": f"€{self._dashboard_data['cost_savings']['daily']:.2f}",
                                  "system_efficiency": f"{self._calculate_overall_health()}%",
                  "next_optimization": self._get_next_optimization_time(),
                  "solar_production_today": f"{random.uniform(15, 25):.1f} kWh",  # Demo data
                  "grid_import_today": f"{random.uniform(8, 15):.1f} kWh",  # Demo data
                  "battery_cycles_today": random.randint(1, 3)  # Demo data
            }
        except Exception as e:
            _LOGGER.error(f"Error generating quick stats: {e}")
            return {}

    def _calculate_overall_health(self):
        """Calculate overall system health percentage."""
        try:
            health_score = 100
            
            # Deduct points for issues
            issues = self._dashboard_data["system_health"]["issues"]
            health_score -= len(issues) * 15
            
            # Factor in efficiency metrics
            solar_util = self._dashboard_data["efficiency_metrics"]["solar_utilization"]
            load_opt = self._dashboard_data["efficiency_metrics"]["load_optimization"]
            
            efficiency_factor = (solar_util + load_opt) / 200  # Normalize to 0-1
            health_score = int(health_score * efficiency_factor)
            
            return max(0, min(100, health_score))
            
        except Exception as e:
            _LOGGER.error(f"Error calculating health score: {e}")
            return 50

    def _get_next_optimization_time(self):
        """Get next scheduled optimization time."""
        try:
            current_time = datetime.now()
            # Optimizations run every 15 minutes
            minutes_to_next = 15 - (current_time.minute % 15)
            next_time = current_time + timedelta(minutes=minutes_to_next)
            return next_time.strftime("%H:%M")
        except Exception as e:
            _LOGGER.error(f"Error getting next optimization time: {e}")
            return "Unknown"


class ScheduleVisualizationSensor(SensorEntity):
    """Sensor for schedule visualization data."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the schedule visualization sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_schedule_visualization"
        self._attr_name = "Schedule Visualization"
        self._attr_unit_of_measurement = "schedules"
        self._state = 0
        
        self._schedule_data = {
            "current_schedule": [],
            "predicted_schedule": [],
            "historical_performance": [],
            "device_timelines": {}
        }

    @property
    def state(self):
        """Return number of active schedules."""
        return len(self._schedule_data["current_schedule"])

    @property
    def extra_state_attributes(self):
        """Return schedule visualization data."""
        return {
            "schedule_data": self._schedule_data,
            "visualization_config": self._get_visualization_config(),
            "chart_ready": True
        }

    async def async_added_to_hass(self):
        """Set up periodic updates."""
        async_track_time_interval(self.hass, self.async_update, timedelta(minutes=5))
        await self.async_update()

    async def async_update(self):
        """Update schedule visualization data."""
        try:
            genetic_algo = self.hass.data.get(DOMAIN, {}).get('genetic_algorithm')
            
            if genetic_algo:
                await self._update_current_schedule(genetic_algo)
                await self._update_predicted_schedule(genetic_algo)
                await self._update_device_timelines(genetic_algo)
            
            self._state = len(self._schedule_data["current_schedule"])
            
        except Exception as e:
            _LOGGER.error(f"Error updating schedule visualization: {e}")

    async def _update_current_schedule(self, genetic_algo):
        """Update current active schedule."""
        try:
            current_schedule = []
            current_time = datetime.now()
            
            # Get current 15-minute slot
            current_slot = (current_time.hour * 4) + (current_time.minute // 15)
            
            # Get device schedules
            for device_id in range(getattr(genetic_algo, 'num_devices', 2)):
                device_state = self.hass.states.get(f"switch.device_{device_id}_schedule")
                if device_state:
                    schedule_attr = device_state.attributes.get('schedule', [])
                    if schedule_attr and current_slot < len(schedule_attr):
                        current_schedule.append({
                            "device_id": device_id,
                            "current_state": device_state.state,
                            "scheduled_value": schedule_attr[current_slot],
                            "next_change": self._find_next_change(schedule_attr, current_slot)
                        })
            
            self._schedule_data["current_schedule"] = current_schedule
            
        except Exception as e:
            _LOGGER.error(f"Error updating current schedule: {e}")

    async def _update_predicted_schedule(self, genetic_algo):
        """Update predicted schedule for next 24 hours."""
        try:
            predicted_schedule = []
            
            # Generate 24-hour prediction (96 x 15-minute slots)
            for slot in range(96):
                time_offset = timedelta(minutes=slot * 15)
                slot_time = datetime.now() + time_offset
                
                # Get pricing for this slot
                pricing_sensor = self.hass.states.get(f"sensor.{DOMAIN}_indexed_pricing")
                if pricing_sensor and 'forecast' in pricing_sensor.attributes:
                    forecast = pricing_sensor.attributes.get('24h_forecast', [])
                    price = forecast[slot // 4] if (slot // 4) < len(forecast) else 0.1
                else:
                    price = 0.1
                
                # Simulate device predictions
                device_predictions = {}
                for device_id in range(getattr(genetic_algo, 'num_devices', 2)):
                    # Simple prediction logic (in real implementation, use GA results)
                    if price < 0.12:
                        device_predictions[f"device_{device_id}"] = 1.0
                    elif price < 0.15:
                        device_predictions[f"device_{device_id}"] = 0.5
                    else:
                        device_predictions[f"device_{device_id}"] = 0.0
                
                predicted_schedule.append({
                    "slot": slot,
                    "time": slot_time.strftime("%H:%M"),
                    "price": price,
                    "devices": device_predictions,
                    "total_load": sum(device_predictions.values()),
                    "solar_forecast": max(0, math.sin(slot * math.pi / 48) * 2)  # Simplified solar curve
                })
            
            self._schedule_data["predicted_schedule"] = predicted_schedule
            
        except Exception as e:
            _LOGGER.error(f"Error updating predicted schedule: {e}")

    async def _update_device_timelines(self, genetic_algo):
        """Update individual device timelines."""
        try:
            device_timelines = {}
            
            for device_id in range(getattr(genetic_algo, 'num_devices', 2)):
                device_name = f"device_{device_id}"
                
                # Get historical data (last 24 hours)
                timeline = []
                for hour in range(24):
                    time_point = datetime.now() - timedelta(hours=23-hour)
                    
                    # Simulate historical data
                    was_on = random.choice([True, False])  # Simplified random choice
                    
                    timeline.append({
                        "time": time_point.strftime("%H:%M"),
                        "timestamp": time_point.isoformat(),
                        "state": "on" if was_on else "off",
                        "power_consumption": 1000 if was_on else 0,  # 1kW when on
                        "cost_impact": 0.1 * 1000 / 1000 if was_on else 0  # €0.10/kWh
                    })
                
                device_timelines[device_name] = {
                    "historical": timeline,
                    "current_state": self.hass.states.get(f"switch.{device_name}_schedule", {}).get("state", "off"),
                    "total_runtime_today": sum(1 for t in timeline if t["state"] == "on"),
                    "energy_consumed_today": sum(t["power_consumption"] for t in timeline) / 1000,  # kWh
                    "cost_today": sum(t["cost_impact"] for t in timeline)
                }
            
            self._schedule_data["device_timelines"] = device_timelines
            
        except Exception as e:
            _LOGGER.error(f"Error updating device timelines: {e}")

    def _find_next_change(self, schedule, current_slot):
        """Find next state change in schedule."""
        try:
            if not schedule or current_slot >= len(schedule):
                return None
            
            current_state = schedule[current_slot]
            for i in range(current_slot + 1, len(schedule)):
                if abs(schedule[i] - current_state) > 0.1:  # State change threshold
                    time_offset = (i - current_slot) * 15  # minutes
                    change_time = datetime.now() + timedelta(minutes=time_offset)
                    return {
                        "time": change_time.strftime("%H:%M"),
                        "new_state": "on" if schedule[i] > 0.5 else "off"
                    }
            return None
        except Exception as e:
            _LOGGER.error(f"Error finding next change: {e}")
            return None

    def _get_visualization_config(self):
        """Get configuration for visualization components."""
        return {
            "chart_types": {
                "schedule_timeline": "gantt",
                "device_usage": "bar",
                "cost_impact": "line",
                "efficiency_trend": "area"
            },
            "colors": {
                "device_0": "#FF6B6B",
                "device_1": "#4ECDC4",
                "solar": "#FFE66D",
                "grid": "#95E1D3",
                "cost": "#F38BA8"
            },
            "time_range": "24h",
            "update_interval": "5min"
        }


async def async_setup_dashboard_sensors(hass: HomeAssistant, entry: ConfigType, async_add_entities: AddEntitiesCallback):
    """Set up dashboard sensors."""
    sensors = [
        OptimizationDashboardSensor(hass, entry.data),
        ScheduleVisualizationSensor(hass, entry.data)
    ]
    
    async_add_entities(sensors)
    _LOGGER.info("Dashboard sensors created successfully")
