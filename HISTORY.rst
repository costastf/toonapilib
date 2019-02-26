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
