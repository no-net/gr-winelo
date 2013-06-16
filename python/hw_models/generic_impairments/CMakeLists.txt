# add the install targets
cmake_minimum_required (VERSION 2.8)
install (FILES
	__init__.py
	awgn_gen.py
	channel_interface.py
    gain.py
    iq_imbalance_gen.py
    phase_noise_gen.py
	DESTINATION ${GR_PYTHON_DIR}/winelo/hw_models/generic_impairments;
)
