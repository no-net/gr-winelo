# add the install targets
add_subdirectory(cost207)
cmake_minimum_required (VERSION 2.8)
install (FILES
	__init__.py
	rayleigh_cc.py
	cs_meas_cc.py
    const_cc.py
	DESTINATION ${GR_PYTHON_DIR}/winelo/channel/models;
)
