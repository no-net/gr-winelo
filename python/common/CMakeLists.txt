# add the install targets
cmake_minimum_required (VERSION 2.8)
install (FILES __init__.py
	libnoise.py
	hwprofile.py
	DESTINATION ${GR_PYTHON_DIR}/winelo/common
)
