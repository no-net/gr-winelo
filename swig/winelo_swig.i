/* -*- c++ -*- */

#define WINELO_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "winelo_swig_doc.i"


%{
#include "winelo_mpc_channel_cc.h"
%}


GR_SWIG_BLOCK_MAGIC(winelo,mpc_channel_cc);
%include "winelo_mpc_channel_cc.h"
