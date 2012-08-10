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
#include <volk/volk.h>
#include <iostream>


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
	set_history(9);
	const int alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
	set_alignment(std::max(1,alignment_multiple));
}


winelo_mpc_channel_cc::~winelo_mpc_channel_cc ()
{
}


int
winelo_mpc_channel_cc::work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items)
{
  	gr_complex *out = (gr_complex *) output_items[0];
  	gr_complex *data = (gr_complex *) input_items[0];
	memset(out,0,noutput_items*sizeof(gr_complex));
  	int noi = noutput_items;
  	
	//delays of the various taps
	int tau_d[] = {0,0,0};
	gr_complex temp[noutput_items];
	if(is_unaligned()) {
		for(size_t i = 1; i < input_items.size(); i++)
			volk_32fc_x2_multiply_32fc_u(temp, (gr_complex*)data+tau_d[i], ((gr_complex*)input_items[i])+tau_d[i], noi);
			volk_32f_x2_add_32f_a((float *)out, (float *)out, (float *)temp, 2*noi);
		}
	else {
		for(size_t i = 1; i < input_items.size(); i++)
		{
			volk_32fc_x2_multiply_32fc_a(temp, (gr_complex*)data+tau_d[i], ((gr_complex*)input_items[i])+tau_d[i], noi);
			volk_32f_x2_add_32f_a((float *)out, (float *)out, (float *)temp, 2*noi);
		}
	}
	return noutput_items;
}

