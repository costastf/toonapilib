=====
Usage
=====


To develop on toonapilib:

.. code-block:: bash

    # The following commands require pipenv as a dependency

    # To lint the project
    _CI/scripts/lint.py

    # To execute the testing
    _CI/scripts/test.py

    # To create a graph of the package and dependency tree
    _CI/scripts/graph.py

    # To build a package of the project under the directory "dist/"
    _CI/scripts/build.py

    # To see the package version
    _CI/scripts/tag.py

    # To bump semantic versioning [--major|--minor|--patch]
    _CI/scripts/tag.py --major|--minor|--patch

    # To upload the project to a pypi repo if user and password are properly provided
    _CI/scripts/upload.py

    # To build the documentation of the project
    _CI/scripts/document.py


To use toonapilib in a project:

.. code-block:: python

    from toonapilib import Toon

    token = '1234-abcdefg-9876654'

    toon = Toon(token)



Print information about the agreement. Attributes are self explanatory.

.. code-block:: python

    print(toon.agreement.id)
    print(toon.agreement.checksum)
    print(toon.agreement.display_common_name)
    print(toon.agreement.display_hardware_version)
    print(toon.agreement.display_software_version)
    print(toon.agreement.heating_type)
    print(toon.agreement.solar)
    print(toon.agreement.toonly)

Print information about the gas. Values are cached internally for 30 seconds so as to not overwhelm the api. After the 30 seconds any access to any of the attributes will refresh the information through a new call to the api.

.. code-block:: python

    print(toon.gas.average_daily)
    print(toon.gas.average)
    print(toon.gas.daily_cost)
    print(toon.gas.daily_usage)
    print(toon.gas.is_smart)
    print(toon.gas.meter_reading)
    print(toon.gas.value)

Print information about the electricity. Values are cached internally for 30 seconds so as to not overwhelm the api. After the 30 seconds any access to any of the attributes will refresh the information through a new call to the api.

.. code-block:: python

    print(toon.power.average_daily)
    print(toon.power.average)
    print(toon.power.daily_cost)
    print(toon.power.daily_usage)
    print(toon.power.is_smart)
    print(toon.power.meter_reading)
    print(toon.power.meter_reading_low)
    print(toon.power.daily_usage_low)
    print(toon.power.value)


Print information about the solar power production. Values are cached internally for 30 seconds so as to not overwhelm the api. After the 30 seconds any access to any of the attributes will refresh the information through a new call to the api.

.. code-block:: python

    print(toon.solar.maximum)
    print(toon.solar.produced)
    print(toon.solar.average_produced)
    print(toon.solar.meter_reading_low_produced)
    print(toon.solar.meter_reading_produced)
    print(toon.solar.daily_cost_produced)
    print(toon.solar.value)

Print information about connected hue lights.

.. code-block:: python

    # loop over all the lights
    for light in toon.lights:
        print(light.is_connected)
        print(light.device_uuid)
        print(light.rgb_color)
        print(light.name)
        print(light.current_state)
        print(light.device_type)
        print(light.in_switch_all_group)
        print(light.in_switch_schedule)
        print(light.is_locked)
        print(light.zwave_index)
        print(light.zwave_uuid)

    # or get a light by assigned name
    light = toon.get_light_by_name('Kitchen Ceiling')

    # print current status
    print(light.status)

    # checking whether the light can be toggled. For that to be able to
    # happen the light needs to be connected and not locked.
    # this state is checked internally from all the methods trying to toggle
    # the switch state of the light
    print(light.can_toggle)

    # lights can be turned on, off or toggled
    light.turn_on()
    light.turn_off()
    light.toggle()

Print information about connected fibaro smart plugs.

.. code-block:: python

    # get first smartplug
    plug = toon.smartplugs[0]

    # or get smartplug by assigned name
    plug = toon.get_smartplug_by_name('Dryer')

    # print all the information about the plug
    print(plug.current_usage)
    print(plug.current_state)
    print(plug.average_usage)
    print(plug.daily_usage)
    print(plug.device_uuid)
    print(plug.is_connected)
    print(plug.name)
    print(plug.network_health_state)
    print(plug.device_type)
    print(plug.in_switch_all_group)
    print(plug.in_switch_schedule)
    print(plug.is_locked)
    print(plug.usage_capable)
    print(plug.zwave_index)
    print(plug.zwave_uuid)
    print(plug.flow_graph_uuid)
    print(plug.quantity_graph_uuid)


    # print current status
    print(plug.status)

    # checking whether the plug can be toggled. For that to be able to
    # happen the plug needs to be connected and not locked.
    # this state is checked internally from all the methods trying to toggle
    # the switch state of the plug
    print(plug.can_toggle)

    # plugs can be turned on, off or toggled
    plug.turn_on()
    plug.turn_off()
    plug.toggle()

Print information about connected smokedetectors.

.. code-block:: python

    # loop over all the smokedetectors
    for smokedetector in toon.smokedetectors:
        print(smokedetector.device_uuid)
        print(smokedetector.name)
        print(smokedetector.last_connected_change)
        print(smokedetector.is_connected)
        print(smokedetector.battery_level)
        print(smokedetector.device_type)


    # or get a smokedetector by assigned name
    smokedetector = toon.get_smokedetector_by_name('Kitchen')


Get the current temperature

.. code-block:: python

    # show the current temperature
    print(toon.temperature)


Work with thermostat states

.. code-block:: python

    # show the information about the current state
    print(toon.thermostat_state.name)
    print(toon.thermostat_state.id)
    print(toon.thermostat_state.temperature)
    print(toon.thermostat_state.dhw)

    # set the current state by using a name out of ['comfort', 'home', 'sleep', away]
    toon.thermostat_state = 'comfort' # Case does not matter. The actual
                                      # values can be overwritten on the
                                      # configuration.py dictionary.


Check out all the thermostat states configured

.. code-block:: python

    for state in toon.thermostat_states:
        print(state.name)
        print(state.id)
        print(state.temperature)
        print(state.dhw)


Work with the thermostat

.. code-block:: python

    # show current value of thermostat
    print(toon.thermostat)

    # manually assign temperature to thermostat. This will override the thermostat state
    toon.thermostat = 20


Exposing flow rrd metrics for for a requested time period

.. code-block:: python

    # Print default time period flow for power and gas
    # from and to arguments can be anything that dateparser can understand. https://dateparser.readthedocs.io/en/latest/
    print(toon.data.flow.get_power_time_window('2 months ago', '3 days ago'))
    print(toon.data.flow.get_gas_time_window('22 nov 2018', '1 jan 2019'))


Exposing graph rrd metrics for a requested time period

.. code-block:: python

    # Print default time period graph for power, gas and district_heat
    # from and to arguments can be anything that dateparser can understand. https://dateparser.readthedocs.io/en/latest/
    print(toon.data.graph.get_power_time_window('2 months ago', '3 days ago', 'weeks'))
    print(toon.data.graph.get_gas_time_window('22 nov 2018', '1 jan 2019', 'days'))
    print(toon.data.graph.get_district_heat_time_window('2 years ago', 'today', 'months'))
