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

#ifndef INCLUDED_WINELO_EVM_CC_H
#define INCLUDED_WINELO_EVM_CC_H

#include <winelo/api.h>
#include <gnuradio/sync_decimator.h>

//class winelo_evm_cc;

//WINELO_API winelo_evm_cc_sptr winelo_make_evm_cc (int vector_length);

/*!
Computes the error vector magntitude.
 */
namespace gr {
    namespace winelo {

        class WINELO_API evm_cc : virtual public sync_decimator
        {
//            friend WINELO_API evm_cc_sptr make_evm_cc (int vector_length);

//            int d_vector_length;
//            int d_alignment_multiple;
//            evm_cc (int vector_length);

        public:
            typedef boost::shared_ptr<evm_cc> sptr;

            static sptr make(int vector_length);
//            ~evm_cc ();


//            int work (int noutput_items,
//                gr_vector_const_void_star &input_items,
//                gr_vector_void_star &output_items);
        };
    }
}

#endif /* INCLUDED_WINELO_EVM_CC_H */

