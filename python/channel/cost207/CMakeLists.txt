# add the install targets
cmake_minimum_required (VERSION 2.8)
install (FILES
	__init__.py
	dopplerspecs.py
	rural_area_cc.py
	DESTINATION ${GR_PYTHON_DIR}/winelo/channel/cost207;
)
