% README for Only Revolutions commentary

* onlyrev/ contains the django project
* onlyrevtext/ is a django application for views interfacing with the text of
  Only Revolutions.

Currently the project uses webfaction for hosting. All details of hosting are
managed by fabric and ``fabfile.py``.

Notes:

* For the map of Sam and Hailey's journey to work properly Django needs to know
  the domain name of the site. Set this in the Site model via the Django admin.
