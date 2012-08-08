# add the install targets
cmake_minimum_required (VERSION 2.8)
install (FILES
	__init__.py
	gauss_rand_proc_f.py
	spec2sos.py
	rayleigh_cc.py
	DESTINATION ${GR_PYTHON_DIR}/winelo/channel;
)
