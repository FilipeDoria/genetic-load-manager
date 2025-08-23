"""Advanced analytics and cost analysis for Genetic Load Manager."""
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.const import CURRENCY_EURO

_LOGGER = logging.getLogger(__name__)
from .const import DOMAIN

class CostAnalyticsSensor(SensorEntity):
    """Advanced cost analysis and financial metrics sensor."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the cost analytics sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_cost_analytics"
        self._attr_name = "Cost Analytics"
        self._attr_unit_of_measurement = CURRENCY_EURO
        self._attr_device_class = "monetary"
        self._attr_state_class = "total"
        self._state = None
        
        # Analytics data storage
        self._cost_data = {
            "daily_costs": [],
            "hourly_breakdown": [],
            "device_costs": {},
            "savings_analysis": {},
            "efficiency_metrics": {},
            "market_analysis": {},
            "forecasts": {},
            "benchmarks": {}
        }
        
        # Historical data for trend analysis
        self._historical_data = []
        self._baseline_data = []
        
    @property
    def state(self):
        """Return total cost savings today."""
        if self._cost_data["savings_analysis"]:
            return self._cost_data["savings_analysis"].get("total_savings_today", 0)
        return 0

    @property
    def extra_state_attributes(self):
        """Return comprehensive cost analytics as attributes."""
        return {
            "cost_data": self._cost_data,
            "chart_data": self._generate_chart_data(),
            "financial_summary": self._generate_financial_summary(),
            "roi_analysis": self._calculate_roi_analysis(),
            "trend_analysis": self._analyze_trends(),
            "last_updated": datetime.now().isoformat()
        }

    async def async_added_to_hass(self):
        """Set up periodic updates for analytics."""
        async_track_time_interval(self.hass, self.async_update, timedelta(minutes=10))
        await self.async_update()

    async def async_update(self):
        """Update cost analytics with latest data."""
        try:
            await self._update_daily_costs()
            await self._update_hourly_breakdown()
            await self._update_device_costs()
            await self._update_savings_analysis()
            await self._update_efficiency_metrics()
            await self._update_market_analysis()
            await self._generate_forecasts()
            await self._update_benchmarks()
            
            # Update state with total savings
            self._state = self._cost_data["savings_analysis"].get("total_savings_today", 0)
            
        except Exception as e:
            _LOGGER.error(f"Error updating cost analytics: {e}")

    async def _update_daily_costs(self):
        """Update daily cost breakdown."""
        try:
            current_date = datetime.now().date()
            
            # Get pricing data
            pricing_sensor = self.hass.states.get(f"sensor.{DOMAIN}_indexed_pricing")
            if not pricing_sensor:
                return
            
            current_price = float(pricing_sensor.state or 0)
            
            # Calculate daily costs (simplified - in real implementation, use actual consumption)
            estimated_daily_consumption = 25.0  # kWh
            optimized_cost = estimated_daily_consumption * current_price
            baseline_cost = estimated_daily_consumption * current_price * 1.15  # 15% higher without optimization
            
            daily_cost_entry = {
                "date": current_date.isoformat(),
                "optimized_cost": round(optimized_cost, 2),
                "baseline_cost": round(baseline_cost, 2),
                "savings": round(baseline_cost - optimized_cost, 2),
                "consumption_kwh": estimated_daily_consumption,
                "avg_price": current_price,
                "optimization_efficiency": 85.0  # Percentage
            }
            
            # Update or add today's entry
            existing_entry = next((entry for entry in self._cost_data["daily_costs"] 
                                 if entry["date"] == current_date.isoformat()), None)
            
            if existing_entry:
                existing_entry.update(daily_cost_entry)
            else:
                self._cost_data["daily_costs"].append(daily_cost_entry)
            
            # Keep only last 30 days
            cutoff_date = (current_date - timedelta(days=30)).isoformat()
            self._cost_data["daily_costs"] = [
                entry for entry in self._cost_data["daily_costs"]
                if entry["date"] >= cutoff_date
            ]
            
        except Exception as e:
            _LOGGER.error(f"Error updating daily costs: {e}")

    async def _update_hourly_breakdown(self):
        """Update hourly cost breakdown for today."""
        try:
            current_hour = datetime.now().hour
            
            # Get pricing data
            pricing_sensor = self.hass.states.get(f"sensor.{DOMAIN}_indexed_pricing")
            if not pricing_sensor:
                return
            
            # Get 24-hour forecast if available
            forecast = pricing_sensor.attributes.get("24h_forecast", [])
            
            hourly_breakdown = []
            for hour in range(24):
                if hour < len(forecast):
                    price = forecast[hour]
                else:
                    price = float(pricing_sensor.state or 0.1)
                
                # Simulate hourly consumption pattern
                consumption = self._simulate_hourly_consumption(hour)
                cost = consumption * price
                
                # Check if devices are scheduled for this hour
                device_status = await self._get_device_status_for_hour(hour)
                
                hourly_breakdown.append({
                    "hour": hour,
                    "price": round(price, 4),
                    "consumption": round(consumption, 2),
                    "cost": round(cost, 2),
                    "device_status": device_status,
                    "is_peak": hour in [18, 19, 20, 21],  # Peak hours
                    "solar_available": max(0, np.sin((hour - 6) * np.pi / 12)) * 2 if 6 <= hour <= 18 else 0
                })
            
            self._cost_data["hourly_breakdown"] = hourly_breakdown
            
        except Exception as e:
            _LOGGER.error(f"Error updating hourly breakdown: {e}")

    async def _update_device_costs(self):
        """Update individual device cost analysis."""
        try:
            device_costs = {}
            
            # Analyze each device
            genetic_algo = self.hass.data.get(DOMAIN, {}).get('genetic_algorithm')
            num_devices = getattr(genetic_algo, 'num_devices', 2)
            
            for device_id in range(num_devices):
                device_name = f"device_{device_id}"
                
                # Get device state
                device_state = self.hass.states.get(f"switch.{device_name}_schedule")
                is_on = device_state and device_state.state == "on"
                
                # Calculate device-specific costs
                power_consumption = 1000  # 1kW default
                hours_on_today = self._estimate_device_runtime(device_id)
                
                pricing_sensor = self.hass.states.get(f"sensor.{DOMAIN}_indexed_pricing")
                avg_price = float(pricing_sensor.state or 0.1) if pricing_sensor else 0.1
                
                daily_cost = (hours_on_today * power_consumption / 1000) * avg_price
                
                device_costs[device_name] = {
                    "current_state": "on" if is_on else "off",
                    "power_consumption_w": power_consumption,
                    "runtime_hours_today": hours_on_today,
                    "energy_consumed_kwh": hours_on_today * power_consumption / 1000,
                    "cost_today": round(daily_cost, 2),
                    "avg_hourly_cost": round(daily_cost / max(hours_on_today, 1), 2),
                    "efficiency_score": np.random.uniform(75, 95),  # Placeholder
                    "optimization_savings": round(daily_cost * 0.15, 2)  # 15% savings estimate
                }
            
            self._cost_data["device_costs"] = device_costs
            
        except Exception as e:
            _LOGGER.error(f"Error updating device costs: {e}")

    async def _update_savings_analysis(self):
        """Update comprehensive savings analysis."""
        try:
            # Calculate various savings metrics
            daily_costs = self._cost_data["daily_costs"]
            if not daily_costs:
                return
            
            # Today's savings
            today_entry = next((entry for entry in daily_costs 
                              if entry["date"] == datetime.now().date().isoformat()), None)
            
            if today_entry:
                total_savings_today = today_entry["savings"]
            else:
                total_savings_today = 0
            
            # Weekly and monthly savings
            week_ago = (datetime.now().date() - timedelta(days=7)).isoformat()
            month_ago = (datetime.now().date() - timedelta(days=30)).isoformat()
            
            weekly_savings = sum(entry["savings"] for entry in daily_costs 
                               if entry["date"] >= week_ago)
            monthly_savings = sum(entry["savings"] for entry in daily_costs 
                                if entry["date"] >= month_ago)
            
            # Savings rate analysis
            total_optimized = sum(entry["optimized_cost"] for entry in daily_costs[-30:])
            total_baseline = sum(entry["baseline_cost"] for entry in daily_costs[-30:])
            savings_rate = ((total_baseline - total_optimized) / total_baseline * 100) if total_baseline > 0 else 0
            
            # Peak hours savings
            peak_savings = self._calculate_peak_hours_savings()
            
            self._cost_data["savings_analysis"] = {
                "total_savings_today": round(total_savings_today, 2),
                "weekly_savings": round(weekly_savings, 2),
                "monthly_savings": round(monthly_savings, 2),
                "annual_projection": round(monthly_savings * 12, 2),
                "savings_rate_percent": round(savings_rate, 1),
                "peak_hours_savings": round(peak_savings, 2),
                "avg_daily_savings": round(monthly_savings / 30, 2),
                "best_day_savings": max((entry["savings"] for entry in daily_costs[-30:]), default=0),
                "consistency_score": self._calculate_savings_consistency()
            }
            
        except Exception as e:
            _LOGGER.error(f"Error updating savings analysis: {e}")

    async def _update_efficiency_metrics(self):
        """Update system efficiency metrics."""
        try:
            # Get genetic algorithm performance data
            genetic_algo = self.hass.data.get(DOMAIN, {}).get('genetic_algorithm')
            
            # Solar utilization efficiency
            solar_efficiency = 0
            if genetic_algo and hasattr(genetic_algo, 'pv_forecast') and genetic_algo.pv_forecast is not None:
                total_solar = np.sum(genetic_algo.pv_forecast)
                if total_solar > 0:
                    # Estimate actual utilization vs available
                    solar_efficiency = np.random.uniform(78, 92)  # Placeholder
            
            # Load optimization efficiency
            load_efficiency = np.random.uniform(82, 95)  # Placeholder
            
            # Battery efficiency (if applicable)
            battery_efficiency = np.random.uniform(85, 95)  # Placeholder
            
            # Overall system efficiency
            overall_efficiency = (solar_efficiency + load_efficiency + battery_efficiency) / 3
            
            self._cost_data["efficiency_metrics"] = {
                "solar_utilization_percent": round(solar_efficiency, 1),
                "load_optimization_percent": round(load_efficiency, 1),
                "battery_efficiency_percent": round(battery_efficiency, 1),
                "overall_system_efficiency": round(overall_efficiency, 1),
                "optimization_convergence_rate": np.random.uniform(85, 98),  # Placeholder
                "algorithm_performance_score": np.random.uniform(88, 96),  # Placeholder
                "energy_waste_reduction": round(np.random.uniform(15, 25), 1)  # Placeholder
            }
            
        except Exception as e:
            _LOGGER.error(f"Error updating efficiency metrics: {e}")

    async def _update_market_analysis(self):
        """Update electricity market analysis."""
        try:
            # Get current and historical pricing
            pricing_sensor = self.hass.states.get(f"sensor.{DOMAIN}_indexed_pricing")
            if not pricing_sensor:
                return
            
            current_price = float(pricing_sensor.state or 0)
            pricing_components = pricing_sensor.attributes.get("pricing_components", {})
            
            # Market price analysis
            market_price = pricing_components.get("market_price", 50)  # €/MWh
            
            # Calculate market trends (simplified)
            price_trend = "stable"  # Could be "rising", "falling", "stable"
            volatility = np.random.uniform(5, 15)  # Price volatility percentage
            
            # Time-of-use analysis
            peak_premium = (current_price * 1.2 - current_price) / current_price * 100
            off_peak_discount = (current_price - current_price * 0.8) / current_price * 100
            
            self._cost_data["market_analysis"] = {
                "current_market_price": market_price,
                "current_final_price": current_price,
                "price_trend": price_trend,
                "volatility_percent": round(volatility, 1),
                "peak_premium_percent": round(peak_premium, 1),
                "off_peak_discount_percent": round(off_peak_discount, 1),
                "market_components": pricing_components,
                "optimal_consumption_hours": self._identify_optimal_hours(),
                "price_forecast_confidence": np.random.uniform(75, 90)  # Placeholder
            }
            
        except Exception as e:
            _LOGGER.error(f"Error updating market analysis: {e}")

    async def _generate_forecasts(self):
        """Generate cost and savings forecasts."""
        try:
            # Generate forecasts based on historical data and trends
            daily_costs = self._cost_data["daily_costs"]
            if len(daily_costs) < 7:
                return  # Need at least a week of data
            
            # Calculate trends
            recent_savings = [entry["savings"] for entry in daily_costs[-7:]]
            avg_daily_savings = np.mean(recent_savings)
            savings_trend = np.polyfit(range(len(recent_savings)), recent_savings, 1)[0]
            
            # Generate forecasts
            forecasts = {
                "next_7_days": {
                    "projected_savings": round(avg_daily_savings * 7, 2),
                    "confidence": 85,
                    "trend": "increasing" if savings_trend > 0 else "decreasing"
                },
                "next_30_days": {
                    "projected_savings": round(avg_daily_savings * 30, 2),
                    "confidence": 75,
                    "seasonal_adjustment": 1.0
                },
                "annual_projection": {
                    "projected_savings": round(avg_daily_savings * 365, 2),
                    "confidence": 65,
                    "factors": ["seasonal_variation", "price_volatility", "usage_patterns"]
                }
            }
            
            self._cost_data["forecasts"] = forecasts
            
        except Exception as e:
            _LOGGER.error(f"Error generating forecasts: {e}")

    async def _update_benchmarks(self):
        """Update performance benchmarks and comparisons."""
        try:
            # Compare against industry benchmarks
            benchmarks = {
                "industry_average_savings": 12.5,  # Percentage
                "top_quartile_savings": 18.0,  # Percentage
                "system_performance_vs_average": 0,  # Will be calculated
                "energy_efficiency_ranking": "above_average",  # Placeholder
                "cost_optimization_score": 0,  # Will be calculated
                "peer_comparison": {
                    "better_than_percent": 0,  # Percentage of similar systems
                    "ranking": "top_25_percent"  # Placeholder
                }
            }
            
            # Calculate our performance vs benchmarks
            our_savings_rate = self._cost_data["savings_analysis"].get("savings_rate_percent", 0)
            
            if our_savings_rate > benchmarks["top_quartile_savings"]:
                benchmarks["energy_efficiency_ranking"] = "excellent"
                benchmarks["peer_comparison"]["ranking"] = "top_10_percent"
                benchmarks["peer_comparison"]["better_than_percent"] = 90
            elif our_savings_rate > benchmarks["industry_average_savings"]:
                benchmarks["energy_efficiency_ranking"] = "above_average"
                benchmarks["peer_comparison"]["ranking"] = "top_25_percent"
                benchmarks["peer_comparison"]["better_than_percent"] = 75
            else:
                benchmarks["energy_efficiency_ranking"] = "average"
                benchmarks["peer_comparison"]["ranking"] = "average"
                benchmarks["peer_comparison"]["better_than_percent"] = 50
            
            benchmarks["system_performance_vs_average"] = round(
                (our_savings_rate / benchmarks["industry_average_savings"] - 1) * 100, 1
            )
            
            benchmarks["cost_optimization_score"] = min(100, max(0, our_savings_rate * 5))  # Scale to 0-100
            
            self._cost_data["benchmarks"] = benchmarks
            
        except Exception as e:
            _LOGGER.error(f"Error updating benchmarks: {e}")

    def _simulate_hourly_consumption(self, hour: int) -> float:
        """Simulate hourly consumption pattern."""
        # Typical household consumption pattern
        base_consumption = 1.0  # kWh
        
        if 6 <= hour <= 8:  # Morning peak
            return base_consumption * 1.5
        elif 18 <= hour <= 22:  # Evening peak
            return base_consumption * 2.0
        elif 0 <= hour <= 6:  # Night
            return base_consumption * 0.6
        else:  # Day hours
            return base_consumption * 0.8

    async def _get_device_status_for_hour(self, hour: int) -> Dict[str, str]:
        """Get device status for specific hour."""
        device_status = {}
        
        for device_id in range(2):  # Assuming 2 devices
            device_state = self.hass.states.get(f"switch.device_{device_id}_schedule")
            if device_state:
                schedule = device_state.attributes.get("schedule", [])
                if hour * 4 < len(schedule):  # Convert hour to 15-min slot
                    status = "on" if schedule[hour * 4] > 0.5 else "off"
                else:
                    status = "off"
            else:
                status = "unknown"
            
            device_status[f"device_{device_id}"] = status
        
        return device_status

    def _estimate_device_runtime(self, device_id: int) -> float:
        """Estimate device runtime for today."""
        # Simplified estimation - in real implementation, track actual runtime
        return np.random.uniform(2, 8)  # 2-8 hours

    def _calculate_peak_hours_savings(self) -> float:
        """Calculate savings specifically during peak hours."""
        # Simplified calculation
        return np.random.uniform(1.5, 4.0)  # €

    def _calculate_savings_consistency(self) -> float:
        """Calculate how consistent the savings are."""
        daily_costs = self._cost_data["daily_costs"]
        if len(daily_costs) < 7:
            return 50.0
        
        savings = [entry["savings"] for entry in daily_costs[-7:]]
        if not savings:
            return 50.0
        
        # Calculate coefficient of variation (lower is more consistent)
        mean_savings = np.mean(savings)
        if mean_savings == 0:
            return 50.0
        
        cv = np.std(savings) / mean_savings
        consistency = max(0, 100 - (cv * 100))  # Convert to 0-100 scale
        
        return round(consistency, 1)

    def _identify_optimal_hours(self) -> List[int]:
        """Identify optimal hours for energy consumption."""
        # Based on pricing data, identify cheapest hours
        pricing_sensor = self.hass.states.get(f"sensor.{DOMAIN}_indexed_pricing")
        if not pricing_sensor:
            return [2, 3, 4, 5, 14, 15]  # Default off-peak hours
        
        forecast = pricing_sensor.attributes.get("24h_forecast", [])
        if not forecast:
            return [2, 3, 4, 5, 14, 15]
        
        # Find hours with lowest prices
        hourly_prices = [(i, price) for i, price in enumerate(forecast[:24])]
        hourly_prices.sort(key=lambda x: x[1])  # Sort by price
        
        optimal_hours = [hour for hour, price in hourly_prices[:6]]  # Top 6 cheapest hours
        return sorted(optimal_hours)

    def _generate_chart_data(self):
        """Generate data formatted for charts and visualizations."""
        try:
            return {
                "daily_savings_trend": {
                    "type": "line",
                    "labels": [entry["date"] for entry in self._cost_data["daily_costs"][-14:]],
                    "datasets": [
                        {
                            "label": "Daily Savings (€)",
                            "data": [entry["savings"] for entry in self._cost_data["daily_costs"][-14:]],
                            "borderColor": "#4CAF50",
                            "backgroundColor": "rgba(76, 175, 80, 0.1)"
                        }
                    ]
                },
                "hourly_cost_breakdown": {
                    "type": "bar",
                    "labels": [f"{hour:02d}:00" for hour in range(24)],
                    "datasets": [
                        {
                            "label": "Hourly Cost (€)",
                            "data": [entry["cost"] for entry in self._cost_data["hourly_breakdown"]],
                            "backgroundColor": [
                                "#FF6B6B" if entry["is_peak"] else "#4ECDC4"
                                for entry in self._cost_data["hourly_breakdown"]
                            ]
                        }
                    ]
                },
                "device_cost_comparison": {
                    "type": "doughnut",
                    "labels": list(self._cost_data["device_costs"].keys()),
                    "datasets": [
                        {
                            "data": [device["cost_today"] for device in self._cost_data["device_costs"].values()],
                            "backgroundColor": ["#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3"]
                        }
                    ]
                },
                "efficiency_radar": {
                    "type": "radar",
                    "labels": ["Solar Utilization", "Load Optimization", "Battery Efficiency", "Overall System"],
                    "datasets": [
                        {
                            "label": "Efficiency %",
                            "data": [
                                self._cost_data["efficiency_metrics"].get("solar_utilization_percent", 0),
                                self._cost_data["efficiency_metrics"].get("load_optimization_percent", 0),
                                self._cost_data["efficiency_metrics"].get("battery_efficiency_percent", 0),
                                self._cost_data["efficiency_metrics"].get("overall_system_efficiency", 0)
                            ],
                            "borderColor": "#2196F3",
                            "backgroundColor": "rgba(33, 150, 243, 0.2)"
                        }
                    ]
                }
            }
        except Exception as e:
            _LOGGER.error(f"Error generating chart data: {e}")
            return {}

    def _generate_financial_summary(self):
        """Generate financial summary for dashboard."""
        try:
            savings = self._cost_data["savings_analysis"]
            return {
                "total_saved_today": f"€{savings.get('total_savings_today', 0):.2f}",
                "monthly_projection": f"€{savings.get('monthly_savings', 0):.2f}",
                "annual_projection": f"€{savings.get('annual_projection', 0):.2f}",
                "savings_rate": f"{savings.get('savings_rate_percent', 0):.1f}%",
                "efficiency_score": f"{self._cost_data['efficiency_metrics'].get('overall_system_efficiency', 0):.1f}%",
                "roi_payback_months": self._calculate_payback_period()
            }
        except Exception as e:
            _LOGGER.error(f"Error generating financial summary: {e}")
            return {}

    def _calculate_roi_analysis(self):
        """Calculate return on investment analysis."""
        try:
            # Simplified ROI calculation
            monthly_savings = self._cost_data["savings_analysis"].get("monthly_savings", 0)
            annual_savings = monthly_savings * 12
            
            # Estimate system cost (placeholder)
            estimated_system_cost = 2000  # €
            
            payback_years = estimated_system_cost / annual_savings if annual_savings > 0 else float('inf')
            roi_percentage = (annual_savings / estimated_system_cost) * 100 if estimated_system_cost > 0 else 0
            
            return {
                "annual_savings": round(annual_savings, 2),
                "system_cost_estimate": estimated_system_cost,
                "payback_period_years": round(payback_years, 1),
                "roi_percentage": round(roi_percentage, 1),
                "net_present_value_10_years": round(annual_savings * 8.5 - estimated_system_cost, 2),  # Simplified NPV
                "internal_rate_of_return": round(roi_percentage, 1)
            }
        except Exception as e:
            _LOGGER.error(f"Error calculating ROI: {e}")
            return {}

    def _analyze_trends(self):
        """Analyze cost and savings trends."""
        try:
            daily_costs = self._cost_data["daily_costs"]
            if len(daily_costs) < 14:
                return {"status": "insufficient_data"}
            
            # Analyze savings trend
            recent_savings = [entry["savings"] for entry in daily_costs[-14:]]
            older_savings = [entry["savings"] for entry in daily_costs[-28:-14]] if len(daily_costs) >= 28 else []
            
            recent_avg = np.mean(recent_savings)
            older_avg = np.mean(older_savings) if older_savings else recent_avg
            
            trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
            trend_magnitude = abs(recent_avg - older_avg) / older_avg * 100 if older_avg > 0 else 0
            
            return {
                "status": "analysis_complete",
                "savings_trend": {
                    "direction": trend_direction,
                    "magnitude_percent": round(trend_magnitude, 1),
                    "recent_average": round(recent_avg, 2),
                    "comparison_average": round(older_avg, 2)
                },
                "volatility": {
                    "coefficient_of_variation": round(np.std(recent_savings) / np.mean(recent_savings) * 100, 1),
                    "stability_rating": "high" if np.std(recent_savings) / np.mean(recent_savings) < 0.2 else "medium"
                },
                "forecast_confidence": 85 if trend_direction != "stable" else 75
            }
        except Exception as e:
            _LOGGER.error(f"Error analyzing trends: {e}")
            return {"status": "error"}

    def _calculate_payback_period(self) -> str:
        """Calculate system payback period in months."""
        try:
            monthly_savings = self._cost_data["savings_analysis"].get("monthly_savings", 0)
            if monthly_savings <= 0:
                return "N/A"
            
            # Estimate system cost (placeholder)
            system_cost = 2000  # €
            payback_months = system_cost / monthly_savings
            
            if payback_months < 12:
                return f"{payback_months:.1f} months"
            else:
                return f"{payback_months/12:.1f} years"
        except Exception as e:
            _LOGGER.error(f"Error calculating payback period: {e}")
            return "N/A"


async def async_setup_analytics_sensors(hass: HomeAssistant, entry: ConfigType, async_add_entities: AddEntitiesCallback):
    """Set up analytics sensors."""
    sensors = [CostAnalyticsSensor(hass, entry.data)]
    async_add_entities(sensors)
    _LOGGER.info("Analytics sensors created successfully")
