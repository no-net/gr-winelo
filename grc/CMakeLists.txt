# Copyright 2011 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

install(FILES
	winelo_mpc_channel_cc.xml
	winelo_sim_sink_c.xml
	winelo_sim_source_c.xml
	winelo_compare_2streams_sink_c.xml
	winelo_mrc_vcc.xml
	winelo_count_samples_cc.xml
	winelo_gauss_rand_proc_c.xml
	winelo_cs_meas_cc.xml
	winelo_rayleigh_cc.xml
	winelo_cost207_rural_area_4paths.xml
	winelo_cost207_typical_urban_6paths.xml
	winelo_cost207_bad_urban_6paths.xml
	winelo_cost207_hilly_terrain_6paths.xml
    	winelo_evm_cc.xml DESTINATION share/gnuradio/grc/blocks
)
