"""Debug service for Genetic Load Manager integration."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.service import async_service_call
from homeassistant.const import ATTR_ENTITY_ID

from .logging_config import log_optimization_summary, log_error_context, log_entity_status, log_data_validation, create_debug_report

_LOGGER = logging.getLogger(__name__)

class GeneticLoadManagerDebugService:
    """Service for debugging Genetic Load Manager optimization issues."""
    
    def __init__(self, hass: HomeAssistant, genetic_algorithm):
        """Initialize the debug service."""
        self.hass = hass
        self.genetic_algorithm = genetic_algorithm
        self.error_history = []
        self.debug_data = {}
        
    async def register_services(self):
        """Register debug services."""
        async def handle_debug_optimization(call: ServiceCall):
            """Handle debug_optimization service call."""
            await self.debug_optimization(call)
        
        async def handle_generate_debug_report(call: ServiceCall):
            """Handle generate_debug_report service call."""
            await self.generate_debug_report(call)
        
        async def handle_validate_entities(call: ServiceCall):
            """Handle validate_entities service call."""
            await self.validate_entities(call)
        
        async def handle_test_data_fetch(call: ServiceCall):
            """Handle test_data_fetch service call."""
            await self.test_data_fetch(call)
        
        async def handle_reset_optimizer(call: ServiceCall):
            """Handle reset_optimizer service call."""
            await self.reset_optimizer(call)
        
        # Register services
        self.hass.services.async_register(
            "genetic_load_manager", "debug_optimization", handle_debug_optimization
        )
        
        self.hass.services.async_register(
            "genetic_load_manager", "generate_debug_report", handle_generate_debug_report
        )
        
        self.hass.services.async_register(
            "genetic_load_manager", "validate_entities", handle_validate_entities
        )
        
        self.hass.services.async_register(
            "genetic_load_manager", "test_data_fetch", handle_test_data_fetch
        )
        
        self.hass.services.async_register(
            "genetic_load_manager", "reset_optimizer", handle_reset_optimizer
        )
        
        _LOGGER.info("Debug services registered successfully")
    
    async def debug_optimization(self, call: ServiceCall):
        """Debug the optimization process step by step."""
        _LOGGER.info("=== Starting optimization debug ===")
        
        try:
            # Step 1: Check genetic algorithm state
            _LOGGER.info("Step 1: Checking genetic algorithm state...")
            ga_state = self._get_genetic_algorithm_state()
            _LOGGER.info(f"Genetic algorithm state: {ga_state}")
            
            # Step 2: Validate configuration
            _LOGGER.info("Step 2: Validating configuration...")
            config_validation = self._validate_configuration()
            for key, value in config_validation.items():
                _LOGGER.info(f"  {key}: {value}")
            
            # Step 3: Check entity availability
            _LOGGER.info("Step 3: Checking entity availability...")
            entity_status = await self._check_entity_availability()
            for entity_id, status in entity_status.items():
                _LOGGER.info(f"  {entity_id}: {status}")
            
            # Step 4: Test data fetching
            _LOGGER.info("Step 4: Testing data fetching...")
            data_fetch_results = await self._test_data_fetching()
            for key, result in data_fetch_results.items():
                _LOGGER.info(f"  {key}: {result}")
            
            # Step 5: Validate data quality
            _LOGGER.info("Step 5: Validating data quality...")
            data_quality = self._validate_data_quality()
            for key, quality in data_quality.items():
                _LOGGER.info(f"  {key}: {quality}")
            
            # Step 6: Test optimization
            _LOGGER.info("Step 6: Testing optimization...")
            optimization_test = await self._test_optimization()
            _LOGGER.info(f"  Optimization test: {optimization_test}")
            
            _LOGGER.info("=== Optimization debug completed ===")
            
            # Store debug results
            self.debug_data['last_debug'] = {
                'timestamp': datetime.now().isoformat(),
                'ga_state': ga_state,
                'config_validation': config_validation,
                'entity_status': entity_status,
                'data_fetch_results': data_fetch_results,
                'data_quality': data_quality,
                'optimization_test': optimization_test
            }
            
        except Exception as e:
            log_error_context(_LOGGER, e, "debug_optimization")
            self._record_error("debug_optimization", e)
    
    async def generate_debug_report(self, call: ServiceCall):
        """Generate a comprehensive debug report."""
        _LOGGER.info("=== Generating debug report ===")
        
        try:
            # Collect all debug information
            report_data = {
                'config': self._get_configuration_summary(),
                'entities': await self._get_entity_summary(),
                'data': self._get_data_summary(),
                'errors': self.error_history[-10:],  # Last 10 errors
                'debug_data': self.debug_data
            }
            
            # Generate report
            report = create_debug_report(_LOGGER, report_data)
            
            # Save report to file
            await self._save_debug_report(report)
            
            _LOGGER.info("Debug report generated and saved successfully")
            
            # Return report in service response
            return {"report": report, "saved": True}
            
        except Exception as e:
            log_error_context(_LOGGER, e, "generate_debug_report")
            self._record_error("generate_debug_report", e)
            return {"error": str(e), "saved": False}
    
    async def validate_entities(self, call: ServiceCall):
        """Validate all configured entities."""
        _LOGGER.info("=== Validating entities ===")
        
        try:
            entities_to_check = call.data.get('entities', [])
            if not entities_to_check:
                # Check all configured entities
                entities_to_check = [
                    self.genetic_algorithm.pv_forecast_today_entity,
                    self.genetic_algorithm.pv_forecast_tomorrow_entity,
                    self.genetic_algorithm.load_forecast_entity,
                    self.genetic_algorithm.battery_soc_entity,
                    self.genetic_algorithm.grid_power_entity
                ]
                entities_to_check = [e for e in entities_to_check if e]
            
            validation_results = {}
            
            for entity_id in entities_to_check:
                try:
                    state = await self.hass.async_add_executor_job(
                        self.hass.states.get, entity_id
                    )
                    
                    if state:
                        validation_results[entity_id] = {
                            'available': True,
                            'state': state.state,
                            'attributes_count': len(state.attributes) if state.attributes else 0,
                            'last_updated': state.last_updated.isoformat() if state.last_updated else None
                        }
                        
                        # Log detailed entity status
                        log_entity_status(_LOGGER, entity_id, state.state, state.attributes)
                    else:
                        validation_results[entity_id] = {
                            'available': False,
                            'error': 'Entity not found'
                        }
                        _LOGGER.error(f"Entity {entity_id} not found")
                        
                except Exception as e:
                    validation_results[entity_id] = {
                        'available': False,
                        'error': str(e)
                    }
                    _LOGGER.error(f"Error validating entity {entity_id}: {e}")
            
            _LOGGER.info("Entity validation completed")
            return validation_results
            
        except Exception as e:
            log_error_context(_LOGGER, e, "validate_entities")
            self._record_error("validate_entities", e)
            return {"error": str(e)}
    
    async def test_data_fetch(self, call: ServiceCall):
        """Test data fetching for all configured entities."""
        _LOGGER.info("=== Testing data fetch ===")
        
        try:
            # Test forecast data fetch
            _LOGGER.info("Testing forecast data fetch...")
            await self.genetic_algorithm.fetch_forecast_data()
            
            # Validate fetched data
            data_validation = self._validate_data_quality()
            
            # Log optimization summary
            summary_data = {
                'availability': {
                    'pv_forecast': self.genetic_algorithm.pv_forecast is not None,
                    'load_forecast': self.genetic_algorithm.load_forecast is not None,
                    'battery_soc': hasattr(self.genetic_algorithm, 'battery_soc'),
                    'pricing': self.genetic_algorithm.pricing is not None
                },
                'quality': data_validation,
                'status': {
                    'population_initialized': hasattr(self.genetic_algorithm, 'population'),
                    'optimization_ready': self._is_optimization_ready()
                }
            }
            
            log_optimization_summary(_LOGGER, summary_data)
            
            _LOGGER.info("Data fetch test completed")
            return summary_data
            
        except Exception as e:
            log_error_context(_LOGGER, e, "test_data_fetch")
            self._record_error("test_data_fetch", e)
            return {"error": str(e)}
    
    async def reset_optimizer(self, call: ServiceCall):
        """Reset the genetic algorithm optimizer."""
        _LOGGER.info("=== Resetting optimizer ===")
        
        try:
            # Stop current optimizer
            if hasattr(self.genetic_algorithm, 'stop'):
                await self.genetic_algorithm.stop()
            
            # Clear population and other state
            if hasattr(self.genetic_algorithm, 'population'):
                delattr(self.genetic_algorithm, 'population')
            
            # Reinitialize
            await self.genetic_algorithm.start()
            
            _LOGGER.info("Optimizer reset successfully")
            return {"status": "reset_successful"}
            
        except Exception as e:
            log_error_context(_LOGGER, e, "reset_optimizer")
            self._record_error("reset_optimizer", e)
            return {"error": str(e)}
    
    def _get_genetic_algorithm_state(self) -> Dict[str, Any]:
        """Get the current state of the genetic algorithm."""
        state = {}
        
        try:
            state['population_initialized'] = hasattr(self.genetic_algorithm, 'population')
            if state['population_initialized']:
                state['population_size'] = len(self.genetic_algorithm.population) if self.genetic_algorithm.population else 0
                state['num_devices'] = self.genetic_algorithm.num_devices
                state['time_slots'] = self.genetic_algorithm.time_slots
            
            state['forecast_data_available'] = {
                'pv_forecast': self.genetic_algorithm.pv_forecast is not None,
                'load_forecast': self.genetic_algorithm.load_forecast is not None,
                'battery_soc': hasattr(self.genetic_algorithm, 'battery_soc'),
                'pricing': self.genetic_algorithm.pricing is not None
            }
            
            state['optimization_ready'] = self._is_optimization_ready()
            
        except Exception as e:
            state['error'] = str(e)
        
        return state
    
    def _validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration."""
        config = {}
        
        try:
            config['optimization_mode'] = getattr(self.genetic_algorithm, 'optimization_mode', 'Not set')
            config['update_interval'] = getattr(self.genetic_algorithm, 'update_interval', 'Not set')
            config['population_size'] = getattr(self.genetic_algorithm, 'population_size', 'Not set')
            config['generations'] = getattr(self.genetic_algorithm, 'generations', 'Not set')
            config['mutation_rate'] = getattr(self.genetic_algorithm, 'mutation_rate', 'Not set')
            config['crossover_rate'] = getattr(self.genetic_algorithm, 'crossover_rate', 'Not set')
            config['num_devices'] = getattr(self.genetic_algorithm, 'num_devices', 'Not set')
            config['time_slots'] = getattr(self.genetic_algorithm, 'time_slots', 'Not set')
            
        except Exception as e:
            config['error'] = str(e)
        
        return config
    
    async def _check_entity_availability(self) -> Dict[str, str]:
        """Check availability of configured entities."""
        entities = {}
        
        try:
            entity_list = [
                ('pv_forecast_today', self.genetic_algorithm.pv_forecast_today_entity),
                ('pv_forecast_tomorrow', self.genetic_algorithm.pv_forecast_tomorrow_entity),
                ('load_forecast', self.genetic_algorithm.load_forecast_entity),
                ('battery_soc', self.genetic_algorithm.battery_soc_entity),
                ('grid_power', self.genetic_algorithm.grid_power_entity)
            ]
            
            for name, entity_id in entity_list:
                if entity_id:
                    try:
                        state = await self.hass.async_add_executor_job(
                            self.hass.states.get, entity_id
                        )
                        if state:
                            entities[entity_id] = f"Available - {state.state}"
                        else:
                            entities[entity_id] = "Not found"
                    except Exception as e:
                        entities[entity_id] = f"Error: {str(e)}"
                else:
                    entities[name] = "Not configured"
                    
        except Exception as e:
            entities['error'] = str(e)
        
        return entities
    
    async def _test_data_fetching(self) -> Dict[str, str]:
        """Test data fetching for all data sources."""
        results = {}
        
        try:
            # Test PV forecast
            if self.genetic_algorithm.pv_forecast_today_entity:
                try:
                    state = await self.hass.async_add_executor_job(
                        self.hass.states.get, self.genetic_algorithm.pv_forecast_today_entity
                    )
                    if state and state.attributes:
                        forecast_data = state.attributes.get("DetailedForecast") or state.attributes.get("DetailedHourly")
                        if forecast_data:
                            results['pv_forecast'] = f"Available - {len(forecast_data)} items"
                        else:
                            results['pv_forecast'] = "No forecast data in attributes"
                    else:
                        results['pv_forecast'] = "Entity unavailable"
                except Exception as e:
                    results['pv_forecast'] = f"Error: {str(e)}"
            else:
                results['pv_forecast'] = "Not configured"
            
            # Test load forecast
            if self.genetic_algorithm.load_forecast_entity:
                try:
                    state = await self.hass.async_add_executor_job(
                        self.hass.states.get, self.genetic_algorithm.load_forecast_entity
                    )
                    if state and state.attributes:
                        forecast_data = state.attributes.get("forecast")
                        if forecast_data:
                            results['load_forecast'] = f"Available - {len(forecast_data)} items"
                        else:
                            results['load_forecast'] = "No forecast data in attributes"
                    else:
                        results['load_forecast'] = "Entity unavailable"
                except Exception as e:
                    results['load_forecast'] = f"Error: {str(e)}"
            else:
                results['load_forecast'] = "Not configured"
            
            # Test battery SOC
            if self.genetic_algorithm.battery_soc_entity:
                try:
                    state = await self.hass.async_add_executor_job(
                        self.hass.states.get, self.genetic_algorithm.battery_soc_entity
                    )
                    if state and state.state not in ['unknown', 'unavailable']:
                        results['battery_soc'] = f"Available - {state.state}"
                    else:
                        results['battery_soc'] = "Entity unavailable"
                except Exception as e:
                    results['battery_soc'] = f"Error: {str(e)}"
            else:
                results['battery_soc'] = "Not configured"
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _validate_data_quality(self) -> Dict[str, Any]:
        """Validate the quality of fetched data."""
        quality = {}
        
        try:
            # Validate PV forecast
            if hasattr(self.genetic_algorithm, 'pv_forecast') and self.genetic_algorithm.pv_forecast:
                pv_data = self.genetic_algorithm.pv_forecast
                quality['pv_forecast'] = {
                    'length': len(pv_data),
                    'expected_length': self.genetic_algorithm.time_slots,
                    'min_value': min(pv_data) if pv_data else None,
                    'max_value': max(pv_data) if pv_data else None,
                    'has_none': any(x is None for x in pv_data) if pv_data else False,
                    'has_inf': any(not (isinstance(x, (int, float)) and x == x and x != float('inf') and x != float('-inf')) for x in pv_data) if pv_data else False
                }
            else:
                quality['pv_forecast'] = "Not available"
            
            # Validate load forecast
            if hasattr(self.genetic_algorithm, 'load_forecast') and self.genetic_algorithm.load_forecast:
                load_data = self.genetic_algorithm.load_forecast
                quality['load_forecast'] = {
                    'length': len(load_data),
                    'expected_length': self.genetic_algorithm.time_slots,
                    'min_value': min(load_data) if load_data else None,
                    'max_value': max(load_data) if load_data else None,
                    'has_none': any(x is None for x in load_data) if load_data else False,
                    'has_inf': any(not (isinstance(x, (int, float)) and x == x and x != float('inf') and x != float('-inf')) for x in load_data) if load_data else False
                }
            else:
                quality['load_forecast'] = "Not available"
            
            # Validate pricing
            if hasattr(self.genetic_algorithm, 'pricing') and self.genetic_algorithm.pricing:
                pricing_data = self.genetic_algorithm.pricing
                quality['pricing'] = {
                    'length': len(pricing_data),
                    'expected_length': self.genetic_algorithm.time_slots,
                    'min_value': min(pricing_data) if pricing_data else None,
                    'max_value': max(pricing_data) if pricing_data else None,
                    'has_none': any(x is None for x in pricing_data) if pricing_data else False,
                    'has_inf': any(not (isinstance(x, (int, float)) and x == x and x != float('inf') and x != float('-inf')) for x in pricing_data) if pricing_data else False
                }
            else:
                quality['pricing'] = "Not available"
                
        except Exception as e:
            quality['error'] = str(e)
        
        return quality
    
    async def _test_optimization(self) -> str:
        """Test if optimization can run successfully."""
        try:
            # Check if all required data is available
            if not self._is_optimization_ready():
                return "Not ready - missing required data"
            
            # Try to run a single generation
            if hasattr(self.genetic_algorithm, 'population') and self.genetic_algorithm.population:
                # Test fitness calculation
                test_chromosome = self.genetic_algorithm.population[0]
                fitness = await self.genetic_algorithm.fitness_function(test_chromosome)
                
                if fitness == -1000.0:
                    return "Fitness calculation failed"
                elif not (isinstance(fitness, (int, float)) and fitness == fitness and fitness != float('inf') and fitness != float('-inf')):
                    return "Fitness calculation returned invalid value"
                else:
                    return f"Ready - fitness test passed: {fitness:.4f}"
            else:
                return "Not ready - population not initialized"
                
        except Exception as e:
            return f"Error during test: {str(e)}"
    
    def _is_optimization_ready(self) -> bool:
        """Check if optimization is ready to run."""
        try:
            required_attrs = ['pv_forecast', 'load_forecast', 'pricing', 'battery_soc']
            
            for attr in required_attrs:
                if not hasattr(self.genetic_algorithm, attr):
                    return False
                if getattr(self.genetic_algorithm, attr) is None:
                    return False
            
            # Check data lengths
            if (len(self.genetic_algorithm.pv_forecast) != self.genetic_algorithm.time_slots or
                len(self.genetic_algorithm.load_forecast) != self.genetic_algorithm.time_slots or
                len(self.genetic_algorithm.pricing) != self.genetic_algorithm.time_slots):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return self._validate_configuration()
    
    async def _get_entity_summary(self) -> Dict[str, str]:
        """Get a summary of entity status."""
        return await self._check_entity_availability()
    
    def _get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of current data."""
        return self._validate_data_quality()
    
    async def _save_debug_report(self, report: str):
        """Save the debug report to a file."""
        try:
            from pathlib import Path
            import os
            
            # Create debug directory
            debug_dir = Path.home() / ".homeassistant" / "logs" / "genetic_load_manager" / "debug"
            debug_dir.mkdir(parents=True, exist_ok=True)
            
            # Save report with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = debug_dir / f"debug_report_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            _LOGGER.info(f"Debug report saved to: {report_file}")
            
        except Exception as e:
            _LOGGER.error(f"Error saving debug report: {e}")
    
    def _record_error(self, context: str, error: Exception):
        """Record an error for the debug report."""
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        
        self.error_history.append(error_record)
        
        # Keep only last 50 errors
        if len(self.error_history) > 50:
            self.error_history = self.error_history[-50:]