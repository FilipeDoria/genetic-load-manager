"""The Genetic Load Manager integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Genetic Load Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # For now, create a simple mock optimizer to test basic functionality
    mock_optimizer = MockOptimizer()
    hass.data[DOMAIN]['optimizer'] = mock_optimizer
    
    # Forward the setup to the platforms using the correct API
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Genetic Load Manager integration setup completed successfully")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    _LOGGER.info("Genetic Load Manager integration unloaded successfully")
    return unload_ok

class MockOptimizer:
    """Mock optimizer for testing basic functionality."""
    
    def __init__(self):
        """Initialize mock optimizer."""
        self.is_running = True
        self.current_generation = 25
        self.best_fitness = 750.0
        self.optimization_count = 5
        self.last_optimization = "2024-01-01T12:00:00"
        self.next_optimization = "2024-01-01T12:15:00"
        self.manageable_loads_count = 3
        self.log_entries_count = 15
    
    def get_status(self):
        """Get mock status."""
        return {
            'is_running': self.is_running,
            'current_generation': self.current_generation,
            'best_fitness': self.best_fitness,
            'optimization_count': self.optimization_count,
            'last_optimization': self.last_optimization,
            'next_optimization': self.next_optimization,
            'manageable_loads_count': self.manageable_loads_count,
            'log_entries_count': self.log_entries_count
        }
    
    def get_logs(self, level=None, limit=10):
        """Get mock logs."""
        return [
            {
                'timestamp': '2024-01-01 12:00:00',
                'level': 'INFO',
                'message': 'Mock optimization completed'
            }
        ] 