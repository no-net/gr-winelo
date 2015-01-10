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

#include <gnuradio/io_signature.h>
#include "mpc_channel_cc_impl.h"
#include <volk/volk.h>
#include <iostream>
#include <fftw3.h>

namespace gr {
    namespace winelo {
        mpc_channel_cc::sptr
        mpc_channel_cc::make(const std::vector<int> &taps_delays, const std::vector<float> &pdp)
        {
            return gnuradio::get_initial_sptr (new mpc_channel_cc_impl(taps_delays, pdp));
        }


        mpc_channel_cc_impl::mpc_channel_cc_impl(const std::vector<int> &taps_delays, const std::vector<float> &pdp)
            : gr::sync_block ("mpc_channel_cc",
                gr::io_signature::make (2, 1+pdp.size(), sizeof (gr_complex)),
                gr::io_signature::make (1, 1, sizeof (gr_complex))),
            d_taps_delays (taps_delays),
            d_pdp (pdp)
        {
            if (d_pdp.size() != taps_delays.size())
            {
                std::cerr << "ERROR: mpc_channel_cc" << std::endl;
                std::cerr << "Length of the power delay power delay profile vector " << \
                        "and the tap delay vector must be equal !" << std::endl;
                exit(1);
            }

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
            else
            {
                for(int i = 0; i < d_taps_delays.size(); i++)
                {
                    d_taps_delays[i]--;
                }
            }
            set_history(max);

            // convert the power delay profile to amplitudes
            for(int i = 0; i < d_pdp.size(); i++)
            {
                d_pdp[i] = sqrt(d_pdp[i]);
            }

            const int alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
            set_alignment(std::max(1,alignment_multiple));
        }

        mpc_channel_cc_impl::~mpc_channel_cc_impl()
        {
        }

        int
        mpc_channel_cc_impl::work (int noutput_items,
                    gr_vector_const_void_star &input_items,
                    gr_vector_void_star &output_items)
        {
            gr_complex *out = (gr_complex *) output_items[0];
            gr_complex *in = (gr_complex *) input_items[0];
            memset(out, 0, noutput_items*sizeof(gr_complex));
            int noi = noutput_items;
            
            gr_complex *temp = (gr_complex*)fftwf_malloc(sizeof(gr_complex)*noutput_items);

            for(size_t i = 0; i < input_items.size()-1; i++)
            {
                gr_complex *vec1_start = in+d_taps_delays[i];
                gr_complex *vec2_start = (gr_complex*)input_items[i+1] + d_taps_delays[i];
                // There are four different cases for the alignment that have to be considered
                // buffers are unaligned and the delay is an even number => call unaligned
                // buffers are aligned and the delay is an odd number => call unaligned
                // buffers are unaligned and the delay is an odd number => call aligned
                // buffers are aligned and the delay is an even number => call aligned
                if ( (is_unaligned() && (d_taps_delays[i]%4 == 0)) || (!is_unaligned() && (d_taps_delays[i]%4 != 0)) )
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
    }
}

