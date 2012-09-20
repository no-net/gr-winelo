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
	d_alignment_multiple = alignment_multiple;
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
	memset(out, 0, noutput_items*sizeof(float));

	int nii = d_win_size;
	gr_complex *temp_c = (gr_complex*)fftwf_malloc(sizeof(gr_complex)*d_win_size);
	float *temp_f = (float*)fftwf_malloc(sizeof(float)*d_win_size);

	// number of processed samples
	int nproc = 0;
	float *in0s = ((float*)in0);
	float *in1s = ((float*)in1);

	bool unalignment = is_unaligned();
	
	std::cout << "work" << std::endl;
	
	for(int k = 0; k < noutput_items; k++)
	{

		if ( unalignment )
		{
			volk_32f_x2_subtract_32f_u((float*)temp_c, in0s, in1s, 2*d_win_size);
			volk_32fc_magnitude_squared_32f_u(temp_f, temp_c, d_win_size);
		}
		else
		{
			volk_32f_x2_subtract_32f_a((float*)temp_c, in0s, in1s, 2*d_win_size);
			volk_32fc_magnitude_squared_32f_a(temp_f, temp_c, d_win_size);
		}
		for(int l = 0; l < d_win_size; l++)
		{
			out[k] += temp_f[l];
		}
		out[k] = out[k]/d_win_size;

		nproc += d_win_size;
		in0s += d_win_size;
		in1s += d_win_size;

		// if the buffers were unaligned from the beginning
		// we never will know when they will be aligned again.
		if (is_unaligned())
			unalignment = true;
		// if the buffers were aligned at the beginning,
		// they will be alligned again iff
		// n*d_win_size = m*d_alignment_multiple
		else if ((nproc % d_alignment_multiple) == 0)
			unalignment = false;
		else
			unalignment = true;
	}
	return noutput_items;
}

