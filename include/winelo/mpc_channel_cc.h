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

#ifndef INCLUDED_WINELO_MPC_CHANNEL_CC_H
#define INCLUDED_WINELO_MPC_CHANNEL_CC_H

#include <winelo/api.h>
#include <gnuradio/sync_block.h>
//#include <gnuradio/types.h>

//class winelo_mpc_channel_cc;

//WINELO_API winelo_mpc_channel_cc_sptr winelo_make_mpc_channel_cc (const std::vector<int> &taps_delays, const std::vector<float> &pdp);

namespace gr {
    namespace winelo {

        /*!
        \brief Models a radio channel with numerous multipath components. The 0th input stream is the signal coming from the transmitter.
        All the other input streams are Gaussian random processes (GRP), where a GRP models the behaviour of all multipath components with an identical delay. The Taps Delays define the difference in delays between the GRP and the power delay profile sets the amplitude of each GRP.
        The taps delays are defined in samples and therefore have to be integer values.
        */
        class WINELO_API mpc_channel_cc : virtual public sync_block
        {
//            friend WINELO_API winelo_mpc_channel_cc_sptr winelo_make_mpc_channel_cc (const std::vector<int> &taps_delays, const std::vector<float> &pdp);

//            std::vector<int>	d_taps_delays;
//            std::vector<float>	d_pdp;

//            winelo_mpc_channel_cc (const std::vector<int> &taps_delays, const std::vector<float> &pdp);

        public:
            typedef boost::shared_ptr<mpc_channel_cc> sptr;

            static sptr make(const std::vector<int> &taps_delays, const std::vector<float> &pdp);
//            ~winelo_mpc_channel_cc ();


//            int work (int noutput_items,
//                gr_vector_const_void_star &input_items,
//                gr_vector_void_star &output_items);
        };
    }
}

#endif /* INCLUDED_WINELO_MPC_CHANNEL_CC_H */

