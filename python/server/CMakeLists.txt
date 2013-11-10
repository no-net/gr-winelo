# add the install targets
cmake_minimum_required (VERSION 2.8)
install (FILES
	__init__.py
	tw2gr_c.py
	gr2tw_c.py
	gr_channel.py
    protocol.py
	DESTINATION ${GR_PYTHON_DIR}/winelo/server
)
