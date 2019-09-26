"""
@package simulator
peer_dbs_simulator module
"""

# Specific simulator behavior.

import sys
import struct
import random
from .common import Common
from .simulator_stuff import Simulator_stuff as sim
#from .simulator_stuff import Simulator_socket as socket
from .socket_wrapper import Socket_wrapper as socket
from .simulator_stuff import hash
from .peer_dbs2 import Peer_DBS2
from .peer_dbs_simulator import Peer_DBS_simulator
import logging
from .chunk_structure import ChunkStructure

#class Peer_DBS2_simulator(Peer_DBS2):
class Peer_DBS2_simulator(Peer_DBS2, Peer_DBS_simulator):

    def __init__(self, id, name = "Peer_DBS2_simulator"):
        Peer_DBS2.__init__(self)
        Peer_DBS_simulator.__init__(self, id, name)
        logging.basicConfig(stream=sys.stdout, format="%(asctime)s.%(msecs)03d %(message)s %(levelname)-8s %(name)s %(pathname)s:%(lineno)d", datefmt="%H:%M:%S")
        self.lg = logging.getLogger(__name__)
        self.lg.setLevel(logging.DEBUG)
        self.name = name
        #colorama.init()
        self.lg.info(f"{name}: DBS2 initialized")

    def send_prune_origin(self, chunk_number, peer):
        Peer_DBS2.send_prune_origin(self, chunk_number, peer)
        self.lg.info(f"{self.ext_id}: [prune {chunk_number}] sent to {peer}")

    def is_duplicate(self, chunk_number):
        Peer_DBS2.is_duplicate(self, chunk_number)
        position = chunk_number % self.buffer_size        
        self.lg.info(f"{self.ext_id}: duplicate {chunk_number} (the first one was originated by {self.buffer[position][ChunkStructure.ORIGIN]})")

    def update_the_team(self, peer):
        Peer_DBS2.update_the_team(self, peer)
        self.lg.info(f"{self.ext_id}: updating team with peer {peer}")

    def process_chunk_received_from_the_splitter(self, chunk_number, origin, chunk_data, sender):
        self.lg.info(f"{self.ext_id}: processing chunk {chunk_number} with origin {origin} received from the splitter")
        Peer_DBS2.process_chunk_received_from_the_splitter(self, chunk_number, origin, chunk_data, sender)
        self.process_chunk__show_fanout()
        self.process_chunk__show_CLR(chunk_number)
        self.number_of_lost_chunks = 0 # ?? Simulator

    def process_chunk(self, chunk_number, origin, chunk_data, sender):
        self.lg.info(f" {self.ext_id}: process_chunk({chunk_number}, {origin}, {chunk_data}, {sender})")
        Peer_DBS2.process_chunk(self, chunk_number, origin, chunk_data, sender)
        
    def request_chunk(self, chunk_number, peer):
        self.lg.info(f"{self.ext_id}: sent [request {chunk_number}] to {peer}")
        Peer_DBS2.request_chunk(self, chunk_number, peer)

    def process_request(self, chunk_number, sender):
        self.lg.info(f"{self.ext_id}: received [request {chunk_number}] from {sender}")
        Peer_DBS2.process_request(self, chunk_number, sender)
        
    def play_chunk__show_buffer(self):
        #sys.stderr.write(f" {len(self.forward)}"); sys.stderr.flush()
        buf = ""
        for i in self.buffer:
            if i[ChunkStructure.CHUNK_DATA] != b'L':
                try:
                    _origin = list(self.team).index(i[ChunkStructure.ORIGIN])
                    buf += hash(_origin)
                except ValueError:
                    buf += '-'  # Does not exist in their forwarding table.
            else:
                buf += " "
        self.lg.debug(f"{self.ext_id}: buffer={buf}")

