"""Support for the Bosch Smart Home system."""
import logging
from urllib.error import HTTPError

import voluptuous as vol

#import BoschShcPy

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_IP_ADDRESS, 
    CONF_PORT,
    CONF_DISCOVERY,
)
from homeassistant.helpers import discovery

from .const import (
    DOMAIN, 
    CONF_ACCESS_CERT, 
    CONF_ACCESS_KEY, 
    SHC_LOGIN,
)

SHC_BRIDGE = "shc_bridge"

_LOGGER = logging.getLogger(__name__)
DEFAULT_DISCOVERY = True

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): cv.string,
                vol.Required(CONF_ACCESS_CERT): cv.string,
                vol.Required(CONF_ACCESS_KEY): cv.string,
                vol.Optional(CONF_PORT, default='8443'): cv.string,
                vol.Optional(CONF_DISCOVERY, default=DEFAULT_DISCOVERY): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    """Set up the Bosch SHC bridge"""
    from BoschShcPy import Client
    _LOGGER.debug("Initializing Bosch SHC bridge")
        
    
    # """Your controller/hub specific code."""
    # # Data that you want to share with your platforms
    hass.data[DOMAIN] = {
        'temperature': 15
    }
    #
    # hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    
    hass.data[SHC_LOGIN] = SHCBridge(hass, config[DOMAIN], Client)
    bridge = hass.data[SHC_LOGIN]
    if not bridge.login():
        _LOGGER.debug("Failed to login to Bosch Smart Home Controller")
        return False
    
    if config[DOMAIN][CONF_DISCOVERY]:
        for component in "sensor", "switch":
            discovery.load_platform(hass, component, DOMAIN, {}, config)
    
    return True


class SHCBridge:
    """A Bosch SHC wrapper class."""

    def __init__(self, hass, domain_config, client):
        """Initialize the Bosch Smart Home Interface."""
        self.config = domain_config
        self._client = client
        self._hass = hass

        self.my_client = client(
            domain_config[CONF_IP_ADDRESS],         domain_config[CONF_PORT], domain_config[CONF_ACCESS_CERT], domain_config[CONF_ACCESS_KEY]
        )

        self._hass.data[SHC_BRIDGE] = self.my_client

    def login(self):
        """Login to SHC."""
        try:
            _LOGGER.debug("Trying to connect to Bosch Smart Home Interface API")
            self.my_client = self._client(
                self.config[CONF_IP_ADDRESS], self.config[CONF_PORT], self.config[CONF_ACCESS_CERT], self.config[CONF_ACCESS_KEY]
            )
            
            shc_info = self.my_client.shc_information()
            _LOGGER.debug('  version        : %s' % shc_info.version)
            _LOGGER.debug('  updateState    : %s' % shc_info.updateState)

            
            return True
        except HTTPError:
            _LOGGER.error("Unable to connect to Bosch Smart Home Interface API")
            return False