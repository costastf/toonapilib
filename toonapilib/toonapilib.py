#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: toonapilib.py
#
# Copyright 2017 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for toonapilib.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

import backoff
import coloredlogs
from cachetools import TTLCache, cached
from requests import Session

from .configuration import (STATES,
                            STATE_CACHING_SECONDS,
                            THERMOSTAT_STATE_CACHING_SECONDS,
                            BURNER_STATES,
                            PROGRAM_STATES)
from .helpers import (Agreement,
                      Light,
                      PowerUsage,
                      SmartPlug,
                      SmokeDetector,
                      Solar,
                      ThermostatInfo,
                      ThermostatState,
                      Usage,
                      Data)
from .toonapilibexceptions import (InvalidAuthenticationToken,
                                   InvalidDisplayName,
                                   InvalidThermostatState,
                                   InvalidProgramState,
                                   IncompleteStatus,
                                   AgreementsRetrievalError)

coloredlogs.auto_install()

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''09-12-2017'''
__copyright__ = '''Copyright 2017, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''toonapilib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())

STATE_CACHE = TTLCache(maxsize=1, ttl=STATE_CACHING_SECONDS)
THERMOSTAT_STATE_CACHE = TTLCache(maxsize=1, ttl=THERMOSTAT_STATE_CACHING_SECONDS)

INVALID_TOKEN = 'Invalid Access Token'


class Toon:  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """Model of the toon smart meter from eneco."""

    def __init__(self,
                 authentication_token,
                 tenant_id='eneco',
                 display_common_name=None):
        logger_name = u'{base}.{suffix}'.format(base=LOGGER_BASENAME,
                                                suffix=self.__class__.__name__)
        self._logger = logging.getLogger(logger_name)
        self._base_url = 'https://api.toon.eu/'
        self._api_url = None
        self.agreements = None
        self.agreement = None
        self._tenant_id = tenant_id
        self._session = self._get_authenticated_session(authentication_token, display_common_name)
        self.data = Data(self)

    def _get_authenticated_session(self, token, display_common_name):
        session = Session()
        session.headers.update({'Authorization': 'Bearer {}'.format(token),
                                'content-type': 'application/json',
                                'cache-control': 'no-cache'})
        agreements = self._get_agreements(session)
        if display_common_name:
            self._logger.debug('Looking for agreement set with display common name %s', display_common_name)
            agreement = next((agreement for agreement in agreements
                              if agreement.display_common_name.lower() == display_common_name.lower()), None)
            if not agreement:
                return InvalidDisplayName(display_common_name)
        else:
            self._logger.debug('No display common name provided, using first agreement retrieved')
            agreement = agreements[0]
        self._logger.debug('Setting appropriate headers for agreement %s', agreement)
        session.headers.update({'X-Common-Name': agreement.display_common_name,
                                'X-Agreement-ID': agreement.id})
        self._api_url = '{}/toon/v3/{}'.format(self._base_url,
                                               agreement.id)
        self.agreements = agreements
        self.agreement = agreement
        return session

    def _get_agreements(self, session):
        url = '{base_url}/toon/v3/agreements'.format(base_url=self._base_url)
        self._logger.debug('Getting agreements from url %s', url)
        agreements_json = {}
        response = session.get(url)
        try:
            agreements_json = response.json()
            self._logger.debug('Got agreements response :%s', agreements_json)
            agreements = [Agreement(agreement.get('agreementId'),
                                    agreement.get('agreementIdChecksum'),
                                    agreement.get('heatingType'),
                                    agreement.get('displayCommonName'),
                                    agreement.get('displayHardwareVersion'),
                                    agreement.get('displaySoftwareVersion'),
                                    agreement.get('isToonSolar'),
                                    agreement.get('isToonly'))
                          for agreement in agreements_json]
        except AttributeError:
            try:
                if agreements_json.get('fault', {}).get('faultstring', {}) == INVALID_TOKEN:
                    raise InvalidAuthenticationToken
            except AttributeError:
                self._logger.debug('Unable to get agreements')
                raise AgreementsRetrievalError(response.text)
        except ValueError:
            self._logger.debug('Unable to get agreements')
            raise AgreementsRetrievalError(response.text)
        return agreements

    @property
    def display_names(self):
        """The ids of all the agreements.

        Returns:
            list: A list of the agreement ids.

        """
        return [agreement.display_common_name.lower() for agreement in self.agreements]

    def _reset(self):
        self.agreements = None
        self.agreement = None

    @property
    @cached(STATE_CACHE)
    @backoff.on_exception(backoff.expo, IncompleteStatus)
    def status(self):
        """The status of toon, cached for 300 seconds."""
        url = '{api_url}/status'.format(api_url=self._api_url)
        response = self._session.get(url)
        if response.status_code == 202:
            self._logger.debug('Response accepted but no data yet, '
                               'trying one more time...')
        response = self._session.get(url)
        try:
            data = response.json()
        except ValueError:
            self._logger.debug('No json on response :%s', response.text)
            raise IncompleteStatus
        return data

    @property
    @cached(THERMOSTAT_STATE_CACHE)
    @backoff.on_exception(backoff.expo, IncompleteStatus)
    def thermostat_states(self):
        """The thermostat states of toon, cached for 1 hour."""
        url = '{api_url}/thermostat/states'.format(api_url=self._api_url)
        response = self._session.get(url)
        if response.status_code == 202:
            self._logger.debug('Response accepted but no data yet, '
                               'trying one more time...')
        response = self._session.get(url)
        try:
            states = response.json().get('state', [])
        except ValueError:
            self._logger.debug('No json on response :%s', response.text)
            raise IncompleteStatus

        return [ThermostatState(STATES[state.get('id')],
                                state.get('id'),
                                state.get('tempValue'),
                                state.get('dhw'))
                for state in states]

    def _clear_cache(self):
        self._logger.debug('Clearing state cache.')
        STATE_CACHE.clear()

    def _get_endpoint_data(self, endpoint, params=None):
        url = '{base}{endpoint}'.format(base=self._api_url,
                                        endpoint=endpoint)

        response = self._session.get(url, params=params)
        if not response.ok:
            self._logger.error(response.content)
            return {}
        self._logger.debug('Response received {}'.format(response.content))
        return response.json()

    @property
    def smokedetectors(self):
        """:return: A list of smokedetector objects modeled as named tuples."""
        return [SmokeDetector(smokedetector.get('devUuid'),
                              smokedetector.get('name'),
                              smokedetector.get('lastConnectedChange'),
                              smokedetector.get('connected'),
                              smokedetector.get('batteryLevel'),
                              smokedetector.get('type'))
                for smokedetector in self.status.get('smokeDetectors',
                                                     {}).get('device', [])]

    def get_smokedetector_by_name(self, name):
        """Retrieves a smokedetector object by its name.

        :param name: The name of the smokedetector to return
        :return: A smokedetector object
        """
        return next((smokedetector for smokedetector in self.smokedetectors
                     if smokedetector.name.lower() == name.lower()), None)

    @property
    def lights(self):
        """:return: A list of light objects."""
        return [Light(self, light.get('name'))
                for light in self.status.get('deviceStatusInfo',
                                             {}).get('device', [])
                if light.get('rgbColor')]

    def get_light_by_name(self, name):
        """Retrieves a light object by its name.

        :param name: The name of the light to return
        :return: A light object
        """
        return next((light for light in self.lights
                     if light.name.lower() == name.lower()), None)

    @property
    def smartplugs(self):
        """:return: A list of smartplug objects."""
        return [SmartPlug(self, plug.get('name'))
                for plug in self.status.get('deviceStatusInfo',
                                            {}).get('device', [])
                if plug.get('networkHealthState')]

    def get_smartplug_by_name(self, name):
        """Retrieves a smartplug object by its name.

        :param name: The name of the smartplug to return
        :return: A smartplug object
        """
        return next((plug for plug in self.smartplugs
                     if plug.name.lower() == name.lower()), None)

    @backoff.on_exception(backoff.expo, IncompleteStatus)
    def _get_status_value(self, value):
        try:
            output = self.status[value]
        except KeyError:
            raise IncompleteStatus(self.status)
        return output

    @property
    def gas(self):
        """:return: A gas object modeled as a named tuple."""
        usage = self._get_status_value('gasUsage')
        return Usage(usage.get('avgDayValue'),
                     usage.get('avgValue'),
                     usage.get('dayCost'),
                     usage.get('dayUsage'),
                     usage.get('isSmart'),
                     usage.get('meterReading'),
                     usage.get('value'))

    @property
    def power(self):
        """:return: A power object modeled as a named tuple."""
        power = self._get_status_value('powerUsage')
        return PowerUsage(power.get('avgDayValue'),
                          power.get('avgValue'),
                          power.get('dayCost'),
                          power.get('dayUsage'),
                          power.get('isSmart'),
                          power.get('meterReading'),
                          power.get('value'),
                          power.get('meterReadingLow'),
                          power.get('dayLowUsage'))

    @property
    def solar(self):
        """:return: A solar object modeled as a named tuple."""
        power = self._get_status_value('powerUsage')
        return Solar(power.get('maxSolar'),
                     power.get('valueProduced'),
                     power.get('valueSolar'),
                     power.get('avgProduValue'),
                     power.get('meterReadingLowProdu'),
                     power.get('meterReadingProdu'),
                     power.get('dayCostProduced'))

    @property
    def thermostat_info(self):
        """:return: A thermostatinfo object modeled as a named tuple."""
        info = self._get_status_value('thermostatInfo')
        return ThermostatInfo(info.get('activeState'),
                              info.get('boilerModuleConnected'),
                              info.get('burnerInfo'),
                              info.get('currentDisplayTemp'),
                              info.get('currentModulationLevel'),
                              info.get('currentSetpoint'),
                              info.get('errorFound'),
                              info.get('haveOTBoiler'),
                              info.get('nextProgram'),
                              info.get('nextSetpoint'),
                              info.get('nextState'),
                              info.get('nextTime'),
                              info.get('otCommError'),
                              info.get('programState'),
                              info.get('realSetpoint'))

    def get_thermostat_state_by_name(self, name):
        """Retrieves a thermostat state object by its assigned name.

        :param name: The name of the thermostat state
        :return: The thermostat state object
        """
        self._validate_thermostat_state_name(name)
        return next((state for state in self.thermostat_states
                     if state.name.lower() == name.lower()), None)

    def get_thermostat_state_by_id(self, id_):
        """Retrieves a thermostat state object by its id.

        :param id_: The id of the thermostat state
        :return: The thermostat state object
        """
        return next((state for state in self.thermostat_states
                     if state.id == id_), None)

    @property
    def burner_on(self):
        """Boolean value of the state of the burner."""
        return bool(self.thermostat_info.burner_info)

    @property
    def burner_state(self):
        """The state the burner is in."""
        return BURNER_STATES.get(int(self.thermostat_info.burner_info))

    @staticmethod
    def _validate_thermostat_state_name(name):
        if name.lower() not in [value.lower() for value in STATES.values()
                                if value.lower() != 'unknown']:
            raise InvalidThermostatState(name)

    @property
    def thermostat_state(self):
        """The state of the thermostat programming.

        :return: A thermostat state object of the current setting
        """
        current_state = self.thermostat_info.active_state
        state = self.get_thermostat_state_by_id(current_state)
        if not state:
            self._logger.debug('Manually set temperature, no Thermostat '
                               'State chosen!')
        return state

    @thermostat_state.setter
    def thermostat_state(self, name):
        """Changes the thermostat state to the one passed as an argument.

        :param name: The name of the thermostat state to change to.
        """
        self._validate_thermostat_state_name(name)
        id_ = next((id_ for id_, state in STATES.items()
                    if state.lower() == name.lower()), None)
        url = '{api_url}/thermostat'.format(api_url=self._api_url)
        data = self._session.get(url).json()
        data["activeState"] = id_
        data["programState"] = 2
        data["currentSetpoint"] = self.get_thermostat_state_by_id(id_).temperature
        response = self._session.put(url, json=data)
        self._logger.debug('Response received {}'.format(response.content))
        self._clear_cache()

    @property
    def thermostat(self):
        """The current setting of the thermostat as temperature.

        :return: A float of the current setting of the temperature of the
        thermostat
        """
        return self.thermostat_info.current_set_point / 100.0

    @thermostat.setter
    def thermostat(self, temperature):
        """A temperature to set the thermostat to. Requires a float.

        :param temperature: A float of the desired temperature to change to.
        """
        try:
            target = int(temperature * 100)
        except ValueError:
            self._logger.error('Please supply a valid temperature e.g: 20')
            return
        url = '{api_url}/thermostat'.format(api_url=self._api_url)
        response = self._session.get(url)
        if not response.ok:
            self._logger.error(response.content)
            return
        data = response.json()
        data["currentSetpoint"] = target
        data["activeState"] = -1
        data["programState"] = 2
        response = self._session.put(url, json=data)
        if not response.ok:
            self._logger.error(response.content)
            return
        self._logger.debug('Response received {}'.format(response.content))
        self._clear_cache()

    @property
    def program_state(self):
        """The active program state of the thermostat.

        :return: the program state
        """
        return PROGRAM_STATES.get(int(self.thermostat_info.program_state))

    @program_state.setter
    def program_state(self, name):
        """Changes the thermostat program state to the one passed as an argument.

        :param name: The program state to change to.
        """
        id_ = next((id_ for id_, state in PROGRAM_STATES.items()
                    if state.lower() == name.lower()), None)
        if id_ is None:
            raise InvalidProgramState(name)
        url = '{api_url}/thermostat'.format(api_url=self._api_url)
        data = self._session.get(url).json()
        data["programState"] = id_
        response = self._session.put(url, json=data)
        self._logger.debug('Response received {}'.format(response.content))
        self._clear_cache()

    @property
    def temperature(self):
        """The current actual temperature as perceived by toon.

        :return: A float of the current temperature
        """
        return self.thermostat_info.current_displayed_temperature / 100.0
