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

#include <winelo_api.h>
#include <gr_sync_decimator.h>

class winelo_evm_cc;
typedef boost::shared_ptr<winelo_evm_cc> winelo_evm_cc_sptr;

WINELO_API winelo_evm_cc_sptr winelo_make_evm_cc (int win_size);

/*!
 * \brief <+description+>
 *
 */
class WINELO_API winelo_evm_cc : public gr_sync_decimator
{
	friend WINELO_API winelo_evm_cc_sptr winelo_make_evm_cc (int win_size);

	int d_win_size;
	int d_alignment_multiple;
	winelo_evm_cc (int win_size);

 public:
	~winelo_evm_cc ();


	int work (int noutput_items,
		gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items);
};

#endif /* INCLUDED_WINELO_EVM_CC_H */

