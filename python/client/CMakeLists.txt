# add the install targets
cmake_minimum_required (VERSION 2.8)
install (FILES
	__init__.py
	client.py
	sim_sink_c.py
	sim_source_c.py
	useful_sinks.py
	useful_blocks.py
	mrc_vcc.py
    tcp_blocks.py
	DESTINATION ${GR_PYTHON_DIR}/winelo/client
)
