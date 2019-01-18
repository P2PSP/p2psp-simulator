"""
@package p2psp-simulator
splitter_sss module
"""
import sys
import time
from threading import Thread

from .common import Common
from .simulator_stuff import Simulator_stuff as sim
from .splitter_strpeds import Splitter_STRPEDS


class Splitter_SSS(Splitter_STRPEDS):
    def __init__(self):
        super().__init__()
        self.t = (len(self.peer_list) // 2) + 1
        print("Splitter SSS initialized")

    def generate_secret_key(self, peer, r):
        # Not needed for simulation
        return NotImplementedError

    def generate_shares(self, secret_key, n):
        # Not needed for simulation
        return NotImplementedError

    def on_round_beginning(self):
        self.remove_outgoing_peers()
        self.punish_peers()
        self.t = (len(self.peer_list) // 2) + 1
        # For each peer in this round:
        #   self.generate_secret_key()
        #   self.generate_shares()

    def say_goodbye(self, peer):
        goodbye = (-1, "G", -1, -1)
        self.team_socket.sendto("isii", goodbye, peer)

    def receive_chunk(self):
        skip = False
        if self.chunk_number == 0:
            last_chunk_sent = Common.MAX_CHUNK_NUMBER - 1
        else:
            last_chunk_sent = self.chunk_number - 1
        step = 0
        while not skip:
            if step > 100:
                print("DIC", self.RECV_LIST.items(), "CHUNK", last_chunk_sent)
                skip = True
            # print("SENT TO", prev_destination, "of", self.peer_list)
            skip = all(v == last_chunk_sent for p, v in sim.RECV_LIST.items())
            time.sleep(0.01)
            step += 1
            # C->Chunk, L->Lost, G->Goodbye, B->Broken, P->Peer, M->Monitor, R-> Ready

        step = 0
        print("++++++++++++++ Receive chunk from SPLITTER +++++++++++++")
        return "C"

    def send_chunk(self, chunk, peer):
        try:
            self.team_socket.sendto("isii", chunk, peer)
        except BlockingIOError:
            sys.stderr.write("sendto: full queue\n")
        else:
            self.chunk_number = (self.chunk_number + 1) % Common.MAX_CHUNK_NUMBER

    def run(self):
        self.setup_peer_connection_socket()
        self.setup_team_socket()

        Thread(target=self.handle_arrivals).start()
        Thread(target=self.moderate_the_team).start()
        Thread(target=self.reset_counters_thread).start()

        while self.alive:
            chunk = self.receive_chunk()

            if self.peer_number == 0:
                self.on_round_beginning()

                sim.FEEDBACK["STATUS"].put(("R", self.current_round))
                sim.FEEDBACK["DRAW"].put(("R", self.current_round))
                sim.FEEDBACK["DRAW"].put(("T", "M", self.number_of_monitors, self.current_round))
                sim.FEEDBACK["DRAW"].put(("T", "P",
                                          (len(self.peer_list) - self.number_of_monitors - self.number_of_malicious),
                                          self.current_round))
                sim.FEEDBACK["DRAW"].put(("T", "MP", self.number_of_malicious, self.current_round))

            try:
                peer = self.peer_list[self.peer_number]
                message = (self.chunk_number, chunk, self.current_round, self.t)
                self.destination_of_chunk.insert(self.chunk_number % self.buffer_size, peer)

                self.send_chunk(message, peer)

                self.compute_next_peer_number(peer)
                print("------> Next Peer Number ----->", self.peer_number)
            except IndexError:
                print("The monitor peer has died!")

            if self.peer_number == 0:
                self.current_round += 1
