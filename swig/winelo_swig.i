/* -*- c++ -*- */

#define WINELO_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "winelo_swig_doc.i"


%{
#include "winelo/mpc_channel_cc.h"
#include "winelo/evm_cc.h"
%}


%include "winelo/mpc_channel_cc.h"
%include "winelo/evm_cc.h"
GR_SWIG_BLOCK_MAGIC2(winelo,mpc_channel_cc);
GR_SWIG_BLOCK_MAGIC2(winelo,evm_cc);
