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

winelo_mpc_channel_cc_sptr
winelo_make_mpc_channel_cc (const std::vector<int> &taps_delays, const std::vector<float> &pdp)
{
	return winelo_mpc_channel_cc_sptr (new winelo_mpc_channel_cc (taps_delays, pdp));
}


winelo_mpc_channel_cc::winelo_mpc_channel_cc (const std::vector<int> &taps_delays, const std::vector<float> &pdp)
	: gr_sync_block ("mpc_channel_cc",
		gr_make_io_signature (2, -1, sizeof (gr_complex)),
		gr_make_io_signature (1, 1, sizeof (gr_complex))),
	d_taps_delays (taps_delays),
	d_pdp (pdp)
{
	int max = 0;
	// get the maximum delay
	for(int i = 0; i < d_taps_delays.size(); i++)
	{
		if (d_taps_delays[i] > max)
			max = d_taps_delays[i];
	}
	// d_taps_delays[i] will be added to the pointer, pointing to the beginning of the input_stream.
	// Since set_history() will add zeros to all input streams the multipath component with the smallest
	// delay in seconds has to be the biggest when being added to the pointer.
	for(int i = 0; i < d_taps_delays.size(); i++)
	{
		d_taps_delays[i] = max - d_taps_delays[i];
	}
	// if max is an even number increment it by one.
	// set_history needs an odd number, otherwise the buffers will be unaligned.
	if(max%2 == 0)
		max += 1;
	set_history(max);

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
	memset(out, 0, noutput_items*sizeof(gr_complex));
  	int noi = noutput_items;
  	
	gr_complex temp[noutput_items];

	for(size_t i = 0; i < input_items.size()-1; i++)
	{
		gr_complex *vec1_start = data+d_taps_delays[i];
		gr_complex *vec2_start = (gr_complex*)input_items[i+1] + d_taps_delays[i];
		// There are four different cases for the alignment that have to be considered
		// buffers are unaligned and the delay is an even number => call unaligned
		// buffers are aligned and the delay is an odd number => call unaligned
		// buffers are unaligned and the delay is an odd number => call aligned
		// buffers are aligned and the delay is an even number => call aligned
		if ( (is_unaligned() && (d_taps_delays[i]%2 == 0)) || (!is_unaligned() && (d_taps_delays[i]%2 != 0)) )
		{
			volk_32fc_x2_multiply_32fc_u(temp, vec1_start, vec2_start, noi);
			volk_32f_s32f_multiply_32f_u((float *)temp, (float *)temp, d_pdp[i], 2*noi);
			volk_32f_x2_add_32f_u((float *)out, (float *)out, (float *)temp, 2*noi);
		}
		else
		{
			volk_32fc_x2_multiply_32fc_a(temp, vec1_start, vec2_start, noi);
			volk_32f_s32f_multiply_32f_a((float *)temp, (float *)temp, d_pdp[i], 2*noi);
			volk_32f_x2_add_32f_a((float *)out, (float *)out, (float *)temp, 2*noi);
		}
	}
	return noutput_items;
}

