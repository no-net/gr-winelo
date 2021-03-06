#
# Copyright 2009 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from gnuradio import gr
import socket
import os


def _get_sock_fd(addr, port, server):
    """
    Get the file descriptor for the socket.
    As a client, block on connect, dup the socket descriptor.
    As a server, block on accept, dup the client descriptor.
    @param addr the ip address string
    @param port the tcp port number
    @param server true for server mode, false for client mode
    @return the file descriptor number
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if server:
        print "DEBUG: SERVER BLK init"
        sock.bind((addr, port))
        sock.listen(1)
        clientsock, address = sock.accept()
        print "DEBUG: SERVER BLK init --- successful!"
        return os.dup(clientsock.fileno())
    else:
        print "DEBUG: CLIENT BLK init"
        sock.connect((addr, port))
        print "DEBUG: CLIENT BLK init --- successful!"
        return os.dup(sock.fileno())


class tcp_source(gr.hier_block2):
    def __init__(self, itemsize, addr, port, server=True):
        #init hier block
        gr.hier_block2.__init__(
            self, 'tcp_source',
            gr.io_signature(0, 0, 0),
            gr.io_signature(1, 1, itemsize),
        )
        fd = _get_sock_fd(addr, port, server)
        self.connect(gr.file_descriptor_source(itemsize, fd), self)


class tcp_sink(gr.hier_block2):
    def __init__(self, itemsize, addr, port, server=False):
        #init hier block
        gr.hier_block2.__init__(
            self, 'tcp_sink',
            gr.io_signature(1, 1, itemsize),
            gr.io_signature(0, 0, 0),
        )
        fd = _get_sock_fd(addr, port, server)
        self.connect(self, gr.file_descriptor_sink(itemsize, fd))
