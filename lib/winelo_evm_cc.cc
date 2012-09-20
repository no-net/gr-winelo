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
#include <winelo_evm_cc.h>
#include <volk/volk.h>

#include <fftw3.h>

#include <iostream>


winelo_evm_cc_sptr
winelo_make_evm_cc (int win_size)
{
	return winelo_evm_cc_sptr (new winelo_evm_cc (win_size));
}


winelo_evm_cc::winelo_evm_cc (int win_size)
	: gr_sync_decimator ("evm_cc",
			     gr_make_io_signature (2, 2, sizeof (gr_complex)),
			     gr_make_io_signature (1, 1, sizeof (float)),
	       		     win_size),
	d_win_size (win_size)
{
	const int alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
	set_alignment(std::max(1,alignment_multiple));
}


winelo_evm_cc::~winelo_evm_cc ()
{
}


int
winelo_evm_cc::work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items)
{
	const gr_complex *in0 = (const gr_complex *) input_items[0];
	const gr_complex *in1 = (const gr_complex *) input_items[1];
	float *out = (float *) output_items[0];

	int nii = d_win_size;
	gr_complex *temp_c = (gr_complex*)fftwf_malloc(sizeof(gr_complex)*d_win_size);
	float *temp_f = (float*)fftwf_malloc(sizeof(float)*d_win_size);

	if ( is_unaligned() )
	{
		std::cout << "unaligned" << std::endl;
		volk_32f_x2_subtract_32f_u((float*)temp_c, (float*)in0, (float*)in1, 2*d_win_size);
		volk_32fc_magnitude_squared_32f_u(temp_f, temp_c, d_win_size);
	}
	else
	{
		volk_32f_x2_subtract_32f_a((float*)temp_c, (float*)in0, (float*)in1, 2*d_win_size);
		volk_32fc_magnitude_squared_32f_a(temp_f, temp_c, d_win_size);
	}
	double sum = 0;
	for( int l = 0; l < d_win_size; l++)
	{
		sum += temp_f[l];
	}
	out[0] = sum;
	return 1;
}

