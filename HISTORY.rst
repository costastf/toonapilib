.. :changelog:

History
-------

0.0.1 (09-12-2017)
---------------------

* First code creation


3.0.2 (16-02-2019)
------------------

* Ported to the latest template. Fixed an issue with the monkey patched requests get method assuming no other process running. Refactored some code to 3.7 specific.


3.0.3 (16-02-2019)
------------------

* Small template cleanup


3.0.4 (16-02-2019)
------------------

* fixed float representation for temperature


3.0.5 (23-02-2019)
------------------

* Tyring to fix library playing well with synology under Home Assistant


3.0.6 (23-02-2019)
------------------

* Fixed dumb bug 


3.0.7 (23-02-2019)
------------------

* re implemented named tuples for python 3.5 and fixed newly introduced bug with token expiry optimization.


3.0.8 (24-02-2019)
------------------

* reverted dataclasses to namedtules for 3.5 compatibility


3.0.9 (24-02-2019)
------------------

* removed unneeded dependency


3.0.10 (26-02-2019)
-------------------

* Disregards program if set to bypass race condition is setting the temperature while program is active


3.0.11 (04-03-2019)
-------------------

* Fixed bug with thermostat state being unsettable with the contribution of John Van De Vrugt https://github.com/JohnvandeVrugt.


3.1.0 (04-03-2019)
------------------

* Implemented data object under toon that exposes flow and graph rrd data for power and gas.


3.2.0 (05-03-2019)
------------------

* Added capabilities to enable/disable thermostat program with the contribution of John Van De Vrugt https://github.com/JohnvandeVrugt.


3.2.1 (06-03-2019)
------------------

* Fixed missplaced files in the root of the virtual environment


3.2.2 (18-03-2019)
------------------

* Changed caching from 30 seconds to 300 seconds due to rate limiting


3.2.3 (11-04-2019)
------------------

* Updating headers according to the upcoming change from Quby


3.2.4 (10-06-2019)
------------------

* Accepted fix from Reinder Reinders ("reinder83") for thermostat states new api endpoint that sometimes is missing from the status response.


3.2.5 (20-10-2019)
------------------

* Removed monkey patching of requests and implemented explicit handling of re authentication.
* Updated tempalate and bumped dependencies.
* Linted.


4.0.0 (30-11-2019)
------------------

* Implemented new token authentication and removed all references to the old authentication method which will not be supported after 01/12/19. Added backoff for some methods.


4.1.0 (30-11-2019)
------------------

* Exposed display names attribute since it is used in Home Assistant internally.


4.1.1 (07-07-2021)
------------------

* Added pipeline and linted.
