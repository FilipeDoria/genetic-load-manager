import asyncio
import logging
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_ON, STATE_OFF, ATTR_ENTITY_ID
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity

# Import your existing optimization code
from data_creation import EMSOptimizer, generate_test_data

_LOGGER = logging.getLogger(__name__)

class EMSTestingIntegration:
    """EMS integration that monitors but doesn't control (testing phase)"""
    
    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.config = config
        self.optimizer = None
        self.monitored_entities = {}
        self.optimization_results = {}
        self.last_optimization = None
        
    async def setup(self):
        """Set up the testing integration"""
        _LOGGER.info("Setting up EMS Testing Integration")
        
        # 1. Set up monitoring (read-only)
        await self._setup_monitoring()
        
        # 2. Create result entities
        await self._create_result_entities()
        
        # 3. Start optimization loop (every 15 minutes)
        asyncio.create_task(self._optimization_loop())
        
        _LOGGER.info("EMS Testing Integration setup complete")
    
    async def _setup_monitoring(self):
        """Monitor real devices without controlling them"""
        entities_to_monitor = [
            'climate.living_room',      # Your AC
            'switch.ev_charger',        # Your EV charger
            'switch.water_heater',      # Your water heater
            'sensor.battery_soc',       # Your battery
            'sensor.grid_import_power', # Grid import
            'sensor.grid_export_power', # Grid export
            'sensor.solar_power',       # Your PV system
        ]
        
        for entity_id in entities_to_monitor:
            if self.hass.states.get(entity_id):
                # Track state changes
                subscription = async_track_state_change(
                    self.hass, entity_id, self._on_state_change
                )
                self.monitored_entities[entity_id] = {
                    'subscription': subscription,
                    'last_state': self.hass.states.get(entity_id)
                }
                _LOGGER.info(f"Monitoring entity: {entity_id}")
            else:
                _LOGGER.warning(f"Entity not found: {entity_id}")
    
    async def _on_state_change(self, entity_id, old_state, new_state):
        """Handle state changes (read-only monitoring)"""
        if new_state:
            self.monitored_entities[entity_id]['last_state'] = new_state
            _LOGGER.debug(f"State change: {entity_id} = {new_state.state}")
    
    async def _create_result_entities(self):
        """Create entities to show optimization results"""
        # Create sensor entities for results
        entities = [
            EMSOptimizationSensor(self.hass, "ems_optimization_status"),
            EMSOptimizationSensor(self.hass, "ems_next_action"),
            EMSOptimizationSensor(self.hass, "ems_estimated_savings"),
            EMSOptimizationSensor(self.hass, "ems_battery_schedule"),
            EMSOptimizationSensor(self.hass, "ems_device_schedule"),
        ]
        
        for entity in entities:
            await entity.async_added_to_hass()
    
    async def _optimization_loop(self):
        """Run optimization every 15 minutes"""
        while True:
            try:
                _LOGGER.info("Starting EMS optimization cycle")
                
                # 1. Collect real data
                real_data = await self._collect_real_data()
                
                # 2. Run optimization (using your existing code)
                schedule, cost = await self._run_optimization(real_data)
                
                # 3. Log results (don't control devices yet)
                await self._log_optimization_results(schedule, cost)
                
                # 4. Update result entities
                await self._update_result_entities(schedule, cost)
                
                # 5. Wait 15 minutes
                await asyncio.sleep(900)  # 15 minutes = 900 seconds
                
            except Exception as e:
                _LOGGER.error(f"Optimization error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _collect_real_data(self) -> dict:
        """Collect real data from your home"""
        data = {}
        
        # Get real device states
        for entity_id, info in self.monitored_entities.items():
            if info['last_state']:
                data[entity_id] = {
                    'state': info['last_state'].state,
                    'attributes': info['last_state'].attributes
                }
        
        # Get real electricity prices (you'd need to set this up)
        data['electricity_prices'] = self._get_electricity_prices()
        
        # Get real weather (if available)
        data['weather'] = self._get_weather_data()
        
        return data
    
    async def _run_optimization(self, real_data: dict):
        """Run your existing optimization code"""
        # Convert real data to format your optimizer expects
        test_data = self._convert_real_to_test_data(real_data)
        
        # Use your existing optimizer
        optimizer = EMSOptimizer(test_data)
        schedule, cost = optimizer.run_ga()
        
        return schedule, cost
    
    def _convert_real_to_test_data(self, real_data: dict):
        """Convert real Home Assistant data to your test data format"""
        # This converts your real device states to the format your optimizer expects
        # You can start with your existing generate_test_data() and modify it
        test_data = generate_test_data()
        
        # Override with real values where available
        if 'sensor.battery_soc' in real_data:
            battery_soc = float(real_data['sensor.battery_soc']['state'])
            test_data['battery']['initial_soc'] = battery_soc
        
        # Add more real data conversions here
        
        return test_data
    
    async def _log_optimization_results(self, schedule, cost):
        """Log what the system would do (without doing it)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"""
=== EMS Optimization Results ({timestamp}) ===
Estimated Daily Cost: {cost:.2f} EUR

Battery Schedule:
{self._format_battery_schedule(schedule)}

Device Schedules:
{self._format_device_schedules(schedule)}

Actions the system WOULD take (but didn't):
{self._format_actions(schedule)}
"""
        
        _LOGGER.info(log_entry)
        
        # Save to a file for review
        with open('/config/ems_optimization_log.txt', 'a') as f:
            f.write(log_entry + "\n")
    
    async def _update_result_entities(self, schedule, cost):
        """Update Home Assistant entities with results"""
        # Update optimization status
        status_entity = self.hass.states.get('sensor.ems_optimization_status')
        if status_entity:
            # Update the entity (you'd need to implement this properly)
            pass
    
    def _format_battery_schedule(self, schedule):
        """Format battery schedule for logging"""
        battery_sched = schedule.get('battery', [])
        formatted = []
        for hour, action in enumerate(battery_sched):
            if action != 0:
                action_type = "CHARGE" if action > 0 else "DISCHARGE"
                formatted.append(f"  Hour {hour:2d}: {action_type} {abs(action):.1f} kW")
        return "\n".join(formatted) if formatted else "  No battery actions planned"
    
    def _format_device_schedules(self, schedule):
        """Format device schedules for logging"""
        formatted = []
        for device_name, device_sched in schedule.items():
            if device_name != 'battery':
                actions = [f"{hour}:{power:.1f}kW" for hour, power in enumerate(device_sched) if power > 0]
                if actions:
                    formatted.append(f"  {device_name}: {', '.join(actions)}")
        return "\n".join(formatted) if formatted else "  No device actions planned"
    
    def _format_actions(self, schedule):
        """Format what actions would be taken"""
        actions = []
        
        # Battery actions
        battery_sched = schedule.get('battery', [])
        for hour, action in enumerate(battery_sched):
            if action > 0:
                actions.append(f"  Hour {hour}: Charge battery at {action:.1f} kW")
            elif action < 0:
                actions.append(f"  Hour {hour}: Discharge battery at {abs(action):.1f} kW")
        
        # Device actions
        for device_name, device_sched in schedule.items():
            if device_name != 'battery':
                for hour, power in enumerate(device_sched):
                    if power > 0:
                        actions.append(f"  Hour {hour}: Turn on {device_name} at {power:.1f} kW")
        
        return "\n".join(actions) if actions else "  No actions planned"
    
    def _get_electricity_prices(self):
        """Get electricity prices (you'd implement this)"""
        # For now, return your test prices
        # Later, you'd get real prices from your utility or API
        return [0.05 + 0.1 * np.sin(2 * np.pi * i / 24 + np.pi) for i in range(24)]
    
    def _get_weather_data(self):
        """Get weather data (you'd implement this)"""
        # For now, return None
        # Later, you'd get real weather from Home Assistant weather entity
        return None