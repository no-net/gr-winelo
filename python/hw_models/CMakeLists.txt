# add the install targets
add_subdirectory(generic_impairments)
cmake_minimum_required (VERSION 2.8)
install (FILES
	__init__.py
	mixing_only_cc.py
	none_cc.py
	basic_cc.py
	DESTINATION ${GR_PYTHON_DIR}/winelo/hw_models;
)
