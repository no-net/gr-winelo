# add the install targets
add_subdirectory(models)
cmake_minimum_required (VERSION 2.8)
install (FILES
	__init__.py
	gauss_rand_proc_c.py
	spec2sos.py
	spec2soc.py
	DESTINATION ${GR_PYTHON_DIR}/winelo/channel;
)
