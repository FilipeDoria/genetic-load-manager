"""Interactive control panel for Genetic Load Manager."""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.const import STATE_ON, STATE_OFF

_LOGGER = logging.getLogger(__name__)
DOMAIN = "genetic_load_manager"

class ControlPanelSensor(SensorEntity):
    """Control panel sensor for interactive genetic load management."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the control panel sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_control_panel"
        self._attr_name = "Genetic Load Manager Control Panel"
        self._attr_unit_of_measurement = "controls"
        self._attr_icon = "mdi:view-dashboard"
        self._state = 0
        
        # Control panel state
        self._control_state = {
            "active_controls": [],
            "available_actions": [],
            "user_preferences": {},
            "quick_actions": [],
            "system_modes": {},
            "parameter_controls": {},
            "schedule_overrides": {},
            "emergency_controls": {}
        }
        
        # User interaction tracking
        self._interaction_history = []
        
    @property
    def state(self):
        """Return number of active controls."""
        return len(self._control_state["active_controls"])

    @property
    def extra_state_attributes(self):
        """Return control panel data as attributes."""
        return {
            "control_state": self._control_state,
            "interaction_history": self._interaction_history[-10:],  # Last 10 interactions
            "panel_config": self._get_panel_configuration(),
            "user_interface": self._get_user_interface_config(),
            "last_updated": datetime.now().isoformat()
        }

    async def async_added_to_hass(self):
        """Set up the control panel."""
        async_track_time_interval(self.hass, self.async_update, timedelta(minutes=2))
        await self._initialize_control_panel()
        await self.async_update()

    async def _initialize_control_panel(self):
        """Initialize control panel with available controls."""
        try:
            genetic_algo = self.hass.data.get(DOMAIN, {}).get('genetic_algorithm')
            
            # Initialize available actions
            self._control_state["available_actions"] = [
                {
                    "id": "run_optimization",
                    "name": "Run Optimization",
                    "description": "Trigger immediate genetic algorithm optimization",
                    "icon": "mdi:play-circle",
                    "category": "optimization",
                    "parameters": {
                        "population_size": {"type": "number", "min": 50, "max": 500, "default": 100},
                        "generations": {"type": "number", "min": 100, "max": 1000, "default": 200},
                        "mutation_rate": {"type": "number", "min": 0.01, "max": 0.2, "default": 0.05, "step": 0.01},
                        "crossover_rate": {"type": "number", "min": 0.5, "max": 0.95, "default": 0.8, "step": 0.05}
                    }
                },
                {
                    "id": "start_optimization",
                    "name": "Start Periodic Optimization",
                    "description": "Start automatic 15-minute optimization cycles",
                    "icon": "mdi:play",
                    "category": "optimization"
                },
                {
                    "id": "stop_optimization",
                    "name": "Stop Optimization",
                    "description": "Stop all optimization processes",
                    "icon": "mdi:stop",
                    "category": "optimization"
                },
                {
                    "id": "toggle_scheduler",
                    "name": "Toggle Scheduler Mode",
                    "description": "Switch between genetic algorithm and rule-based scheduling",
                    "icon": "mdi:swap-horizontal",
                    "category": "scheduling",
                    "parameters": {
                        "mode": {"type": "select", "options": ["genetic", "rule-based"], "default": "genetic"}
                    }
                },
                {
                    "id": "update_pricing",
                    "name": "Update Pricing Parameters",
                    "description": "Modify indexed tariff pricing components",
                    "icon": "mdi:currency-eur",
                    "category": "pricing",
                    "parameters": {
                        "mfrr": {"type": "number", "min": 0, "max": 10, "default": 1.94, "step": 0.01, "unit": "€/MWh"},
                        "q": {"type": "number", "min": 0, "max": 100, "default": 30, "step": 0.1, "unit": "€/MWh"},
                        "fp": {"type": "number", "min": 1, "max": 2, "default": 1.1674, "step": 0.0001},
                        "tae": {"type": "number", "min": 0, "max": 200, "default": 60, "step": 0.1, "unit": "€/MWh"},
                        "vat": {"type": "number", "min": 1, "max": 1.5, "default": 1.23, "step": 0.01},
                        "peak_multiplier": {"type": "number", "min": 1, "max": 2, "default": 1.2, "step": 0.1},
                        "off_peak_multiplier": {"type": "number", "min": 0.5, "max": 1, "default": 0.8, "step": 0.1}
                    }
                }
            ]
            
            # Initialize quick actions
            self._control_state["quick_actions"] = [
                {"id": "emergency_stop", "name": "Emergency Stop", "icon": "mdi:emergency-stop", "color": "red"},
                {"id": "quick_optimize", "name": "Quick Optimize", "icon": "mdi:flash", "color": "green"},
                {"id": "reset_system", "name": "Reset System", "icon": "mdi:restart", "color": "orange"},
                {"id": "export_data", "name": "Export Data", "icon": "mdi:download", "color": "blue"}
            ]
            
            # Initialize system modes
            self._control_state["system_modes"] = {
                "current_mode": "automatic",
                "available_modes": [
                    {"id": "automatic", "name": "Automatic", "description": "Full genetic algorithm control"},
                    {"id": "manual", "name": "Manual", "description": "User-controlled device scheduling"},
                    {"id": "eco", "name": "Eco Mode", "description": "Maximum energy savings priority"},
                    {"id": "comfort", "name": "Comfort Mode", "description": "User comfort priority"},
                    {"id": "maintenance", "name": "Maintenance", "description": "System maintenance mode"}
                ]
            }
            
            # Initialize parameter controls
            if genetic_algo:
                self._control_state["parameter_controls"] = {
                    "population_size": {
                        "current": getattr(genetic_algo, 'population_size', 100),
                        "min": 50, "max": 500, "step": 10
                    },
                    "generations": {
                        "current": getattr(genetic_algo, 'generations', 200),
                        "min": 100, "max": 1000, "step": 50
                    },
                    "mutation_rate": {
                        "current": getattr(genetic_algo, 'mutation_rate', 0.05),
                        "min": 0.01, "max": 0.2, "step": 0.01
                    },
                    "crossover_rate": {
                        "current": getattr(genetic_algo, 'crossover_rate', 0.8),
                        "min": 0.5, "max": 0.95, "step": 0.05
                    }
                }
            
            # Initialize schedule overrides
            self._control_state["schedule_overrides"] = {
                "active_overrides": [],
                "override_types": [
                    {"id": "force_on", "name": "Force Device On", "icon": "mdi:power-on"},
                    {"id": "force_off", "name": "Force Device Off", "icon": "mdi:power-off"},
                    {"id": "schedule_delay", "name": "Delay Schedule", "icon": "mdi:clock-plus"},
                    {"id": "priority_boost", "name": "Priority Boost", "icon": "mdi:arrow-up-bold"}
                ]
            }
            
            # Initialize emergency controls
            self._control_state["emergency_controls"] = {
                "emergency_stop": {"available": True, "description": "Stop all automated control"},
                "safe_mode": {"available": True, "description": "Switch to safe manual mode"},
                "system_reset": {"available": True, "description": "Reset to default settings"},
                "backup_restore": {"available": True, "description": "Restore from backup"}
            }
            
            _LOGGER.info("Control panel initialized successfully")
            
        except Exception as e:
            _LOGGER.error(f"Error initializing control panel: {e}")

    async def async_update(self):
        """Update control panel state."""
        try:
            await self._update_active_controls()
            await self._update_system_status()
            await self._cleanup_old_interactions()
            
            self._state = len(self._control_state["active_controls"])
            
        except Exception as e:
            _LOGGER.error(f"Error updating control panel: {e}")

    async def _update_active_controls(self):
        """Update list of currently active controls."""
        try:
            active_controls = []
            
            # Check optimization status
            genetic_algo = self.hass.data.get(DOMAIN, {}).get('genetic_algorithm')
            if genetic_algo and hasattr(genetic_algo, 'is_running') and genetic_algo.is_running:
                active_controls.append({
                    "id": "optimization_running",
                    "name": "Optimization Active",
                    "type": "status",
                    "icon": "mdi:cog-play",
                    "color": "green"
                })
            
            # Check device controls
            for device_id in range(2):  # Assuming 2 devices
                device_state = self.hass.states.get(f"switch.device_{device_id}_schedule")
                if device_state and device_state.state == STATE_ON:
                    active_controls.append({
                        "id": f"device_{device_id}_active",
                        "name": f"Device {device_id} Scheduled",
                        "type": "device",
                        "icon": "mdi:power-plug",
                        "color": "blue"
                    })
            
            # Check for any overrides
            for override in self._control_state["schedule_overrides"]["active_overrides"]:
                active_controls.append({
                    "id": f"override_{override['id']}",
                    "name": f"Override: {override['name']}",
                    "type": "override",
                    "icon": "mdi:hand-back-right",
                    "color": "orange"
                })
            
            self._control_state["active_controls"] = active_controls
            
        except Exception as e:
            _LOGGER.error(f"Error updating active controls: {e}")

    async def _update_system_status(self):
        """Update overall system status for control panel."""
        try:
            # Get system health
            dashboard_sensor = self.hass.states.get(f"sensor.{DOMAIN}_dashboard")
            if dashboard_sensor:
                dashboard_data = dashboard_sensor.attributes.get('dashboard_data', {})
                system_health = dashboard_data.get('system_health', {})
                
                # Update system modes based on health
                if system_health.get('status') == 'error':
                    self._control_state["system_modes"]["current_mode"] = "maintenance"
                elif len(system_health.get('issues', [])) > 0:
                    self._control_state["system_modes"]["current_mode"] = "manual"
            
            # Update parameter controls with current values
            genetic_algo = self.hass.data.get(DOMAIN, {}).get('genetic_algorithm')
            if genetic_algo:
                for param in self._control_state["parameter_controls"]:
                    if hasattr(genetic_algo, param):
                        self._control_state["parameter_controls"][param]["current"] = getattr(genetic_algo, param)
            
        except Exception as e:
            _LOGGER.error(f"Error updating system status: {e}")

    async def _cleanup_old_interactions(self):
        """Clean up old interaction history."""
        try:
            # Keep only interactions from last 24 hours
            cutoff = datetime.now() - timedelta(hours=24)
            self._interaction_history = [
                interaction for interaction in self._interaction_history
                if datetime.fromisoformat(interaction["timestamp"]) > cutoff
            ]
        except Exception as e:
            _LOGGER.error(f"Error cleaning up interactions: {e}")

    def _get_panel_configuration(self):
        """Get control panel UI configuration."""
        return {
            "layout": "grid",
            "columns": 3,
            "theme": "genetic_load_manager",
            "sections": [
                {
                    "id": "quick_actions",
                    "name": "Quick Actions",
                    "position": {"row": 1, "col": 1, "span": 1},
                    "type": "button_grid"
                },
                {
                    "id": "system_status",
                    "name": "System Status",
                    "position": {"row": 1, "col": 2, "span": 1},
                    "type": "status_display"
                },
                {
                    "id": "parameter_controls",
                    "name": "Parameter Controls",
                    "position": {"row": 1, "col": 3, "span": 1},
                    "type": "slider_controls"
                },
                {
                    "id": "device_controls",
                    "name": "Device Controls",
                    "position": {"row": 2, "col": 1, "span": 2},
                    "type": "device_grid"
                },
                {
                    "id": "schedule_overrides",
                    "name": "Schedule Overrides",
                    "position": {"row": 2, "col": 3, "span": 1},
                    "type": "override_panel"
                },
                {
                    "id": "emergency_controls",
                    "name": "Emergency Controls",
                    "position": {"row": 3, "col": 1, "span": 3},
                    "type": "emergency_bar"
                }
            ]
        }

    def _get_user_interface_config(self):
        """Get user interface configuration for frontend."""
        return {
            "color_scheme": {
                "primary": "#2196F3",
                "secondary": "#4CAF50",
                "warning": "#FF9800",
                "error": "#F44336",
                "success": "#8BC34A"
            },
            "button_styles": {
                "quick_action": {"size": "large", "style": "filled"},
                "parameter": {"size": "medium", "style": "outlined"},
                "emergency": {"size": "large", "style": "filled", "color": "error"}
            },
            "animations": {
                "enabled": True,
                "duration": "300ms",
                "easing": "ease-in-out"
            },
            "responsive": {
                "mobile_breakpoint": "768px",
                "tablet_breakpoint": "1024px"
            }
        }

    async def log_user_interaction(self, action_id: str, parameters: Dict[str, Any] = None, user_id: str = None):
        """Log user interaction with control panel."""
        try:
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "action_id": action_id,
                "parameters": parameters or {},
                "user_id": user_id or "unknown",
                "success": True,
                "response_time": 0  # Will be updated when action completes
            }
            
            self._interaction_history.append(interaction)
            _LOGGER.info(f"User interaction logged: {action_id}")
            
        except Exception as e:
            _LOGGER.error(f"Error logging user interaction: {e}")

    async def execute_control_action(self, action_id: str, parameters: Dict[str, Any] = None):
        """Execute a control panel action."""
        try:
            start_time = datetime.now()
            
            # Log the interaction
            await self.log_user_interaction(action_id, parameters)
            
            # Execute the action
            success = False
            if action_id == "run_optimization":
                success = await self._execute_run_optimization(parameters or {})
            elif action_id == "start_optimization":
                success = await self._execute_start_optimization()
            elif action_id == "stop_optimization":
                success = await self._execute_stop_optimization()
            elif action_id == "toggle_scheduler":
                success = await self._execute_toggle_scheduler(parameters or {})
            elif action_id == "update_pricing":
                success = await self._execute_update_pricing(parameters or {})
            elif action_id == "emergency_stop":
                success = await self._execute_emergency_stop()
            elif action_id == "quick_optimize":
                success = await self._execute_quick_optimize()
            elif action_id == "reset_system":
                success = await self._execute_reset_system()
            elif action_id == "export_data":
                success = await self._execute_export_data()
            else:
                _LOGGER.warning(f"Unknown control action: {action_id}")
                return False
            
            # Update interaction history with result
            if self._interaction_history:
                self._interaction_history[-1]["success"] = success
                self._interaction_history[-1]["response_time"] = (datetime.now() - start_time).total_seconds()
            
            return success
            
        except Exception as e:
            _LOGGER.error(f"Error executing control action {action_id}: {e}")
            return False

    async def _execute_run_optimization(self, parameters: Dict[str, Any]) -> bool:
        """Execute run optimization action."""
        try:
            service_data = {}
            for param, value in parameters.items():
                if param in ['population_size', 'generations', 'mutation_rate', 'crossover_rate']:
                    service_data[param] = value
            
            await self.hass.services.async_call(
                DOMAIN, "run_optimization", service_data
            )
            return True
        except Exception as e:
            _LOGGER.error(f"Error running optimization: {e}")
            return False

    async def _execute_start_optimization(self) -> bool:
        """Execute start optimization action."""
        try:
            await self.hass.services.async_call(DOMAIN, "start_optimization", {})
            return True
        except Exception as e:
            _LOGGER.error(f"Error starting optimization: {e}")
            return False

    async def _execute_stop_optimization(self) -> bool:
        """Execute stop optimization action."""
        try:
            await self.hass.services.async_call(DOMAIN, "stop_optimization", {})
            return True
        except Exception as e:
            _LOGGER.error(f"Error stopping optimization: {e}")
            return False

    async def _execute_toggle_scheduler(self, parameters: Dict[str, Any]) -> bool:
        """Execute toggle scheduler action."""
        try:
            mode = parameters.get('mode', 'genetic')
            await self.hass.services.async_call(
                DOMAIN, "toggle_scheduler", {"mode": mode}
            )
            return True
        except Exception as e:
            _LOGGER.error(f"Error toggling scheduler: {e}")
            return False

    async def _execute_update_pricing(self, parameters: Dict[str, Any]) -> bool:
        """Execute update pricing action."""
        try:
            await self.hass.services.async_call(
                DOMAIN, "update_pricing_parameters", parameters
            )
            return True
        except Exception as e:
            _LOGGER.error(f"Error updating pricing: {e}")
            return False

    async def _execute_emergency_stop(self) -> bool:
        """Execute emergency stop action."""
        try:
            # Stop optimization
            await self.hass.services.async_call(DOMAIN, "stop_optimization", {})
            
            # Turn off all scheduled devices
            for device_id in range(2):
                device_entity = f"switch.device_{device_id}_schedule"
                if self.hass.states.get(device_entity):
                    await self.hass.services.async_call(
                        "switch", "turn_off", {"entity_id": device_entity}
                    )
            
            _LOGGER.warning("Emergency stop executed - all optimization stopped")
            return True
        except Exception as e:
            _LOGGER.error(f"Error executing emergency stop: {e}")
            return False

    async def _execute_quick_optimize(self) -> bool:
        """Execute quick optimization with default parameters."""
        try:
            await self.hass.services.async_call(
                DOMAIN, "run_optimization", 
                {"population_size": 50, "generations": 100}
            )
            return True
        except Exception as e:
            _LOGGER.error(f"Error executing quick optimize: {e}")
            return False

    async def _execute_reset_system(self) -> bool:
        """Execute system reset action."""
        try:
            # Stop optimization
            await self.hass.services.async_call(DOMAIN, "stop_optimization", {})
            
            # Reset to default parameters
            genetic_algo = self.hass.data.get(DOMAIN, {}).get('genetic_algorithm')
            if genetic_algo:
                genetic_algo.population_size = 100
                genetic_algo.generations = 200
                genetic_algo.mutation_rate = 0.05
                genetic_algo.crossover_rate = 0.8
            
            _LOGGER.info("System reset executed")
            return True
        except Exception as e:
            _LOGGER.error(f"Error executing system reset: {e}")
            return False

    async def _execute_export_data(self) -> bool:
        """Execute data export action."""
        try:
            await self.hass.services.async_call(
                DOMAIN, "export_schedule", {"format": "json", "include_metadata": True}
            )
            return True
        except Exception as e:
            _LOGGER.error(f"Error executing data export: {e}")
            return False


async def async_setup_control_panel_sensors(hass: HomeAssistant, entry: ConfigType, async_add_entities: AddEntitiesCallback):
    """Set up control panel sensors."""
    sensors = [ControlPanelSensor(hass, entry.data)]
    async_add_entities(sensors)
    _LOGGER.info("Control panel sensors created successfully")
