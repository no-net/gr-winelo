/* -*- c++ -*- */
/* 
 * Copyright 2012 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_io_signature.h>
#include <winelo_mpc_channel_cc.h>


winelo_mpc_channel_cc_sptr
winelo_make_mpc_channel_cc ()
{
	return winelo_mpc_channel_cc_sptr (new winelo_mpc_channel_cc ());
}


winelo_mpc_channel_cc::winelo_mpc_channel_cc ()
	: gr_sync_block ("mpc_channel_cc",
		gr_make_io_signature (2, -1, sizeof (gr_complex)),
		gr_make_io_signature (1, 1, sizeof (gr_complex)))
{
}


winelo_mpc_channel_cc::~winelo_mpc_channel_cc ()
{
}


int
winelo_mpc_channel_cc::work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items)
{
	const float *in0 = (const float *) input_items[0];
	const float *in1 = (const float *) input_items[1];
	float *out = (float *) output_items[0];

	for (int i = 0; i < noutput_items; i++){
		out[i] = in0[i] * in1[i];
	}

	return noutput_items;
}

