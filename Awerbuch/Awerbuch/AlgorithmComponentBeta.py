"""
Awerbuch’s synchronizers alpha guarantees local synchronization,
"""


import queue
import logging
import time
import random
from time import sleep

from enum import Enum

from adhoccomputing.GenericModel import EventTypes, GenericModel, Event
from adhoccomputing.Generics import ConnectorList, ConnectorTypes
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

import threading

from BaseComponent import BaseComponent

logger = logging.getLogger("AHC")




class AlgorithmComponentBeta(BaseComponent):
    """Awerbuch’s synchronizers alpha guarantees local synchronization,
    """
    end_time = -1
    def on_init(self, eventobj: Event):
        """On init function that initiates neccessary variables
        and initiates the algorithm with new round event
        """
        super().on_init(eventobj)
        self.lock = threading.Lock()
        self.adjnd = {}
        for edge in (self.topology.G.edges):
            if self.componentinstancenumber == edge[0]:
                self.adjnd[edge[1]] = False
            elif self.componentinstancenumber == edge[1]:
                self.adjnd[edge[0]] = False
            
        self.round = 0
        self.last_round = 10
        self.messages_to_be_send = {}
        self.messages_received = {}
        self.ended = False
        self.root = False
        if self.componentinstancenumber == 0:
            self.root = True
            self.all_nodes = set(self.topology.G.nodes)
            self.all_nodes.remove(0)
            self.adjok = set()

        self.new_round_event()
        self.timer_thread = threading.Thread(target=self.periodic_messages)
        self.timer_thread.start()
        # task_thread.join()

    
    def periodic_messages(self):
        while not self.ended:
            time.sleep(0.01)
            with self.lock:
                self.send_all_my_messages()
    
    def send_all_my_messages(self):
        for neighboor, (round, message) in self.messages_to_be_send.items():
            if self.adjnd[neighboor] == False:
                self.send_message_event( 
                        EventTypes.MFRT,
                        neighboor,
                        message,
                        nexthop=neighboor,
                    )

    def new_round_event(self):
        """ Local round event that works by
        first resetting state of operations
        then multicasting the start to neighboors of the new local round
        """
        with self.lock:
            self.round += 1
            if self.round > self.last_round:
                self.ended = True
                AlgorithmComponentBeta.end_time = time.time()
            else:
                # print('new round')
                self.unreceived_count = len(self.adjnd)
                if self.root:
                    self.nonOK_count = len(self.all_nodes)
                for i in self.adjnd:
                    self.adjnd[i] = False
                    self.messages_to_be_send[i] = (self.round, f'{self.round}#{self.round}')
                    self.messages_received[i] = (None)
                self.send_all_my_messages()
        
        # if self.ended:
        #     self.timer_thread.join()
        


    def on_message_from_bottom(self, eventobj: Event):
        """ Checks received messages from and if neccessary(every node sent messaage) initiates next round
        """
        super().on_message_from_bottom(eventobj)
        if not self.ended:
            if self.componentinstancenumber == eventobj.eventcontent.header.messageto:
                neighboor = eventobj.eventsource_componentinstancenumber
                message, other_round = eventobj.eventcontent.payload.messagepayload.split('#')
                other_round = int(other_round)
                if message.isnumeric():
                    if other_round == self.round:
                        self.send_message_event( 
                            EventTypes.MFRT,
                            neighboor,
                            f'ACK#{self.round}',
                            nexthop=neighboor,
                        )   
                elif other_round >= self.round:
                    if message == 'ACK' and self.adjnd[neighboor] == False:
                        self.adjnd[neighboor] = True
                        self.unreceived_count -= 1
                    elif message == 'OK' and self.adjok[neighboor] == False:
                        self.on_OK_message(neighboor)
                    elif message == 'GO':
                        self.new_round_event()
                    if self.root and not self.nonOK_count and not self.unreceived_count:
                        self.broadcast_go(self.round + 1)
                
                self.round_end_check()
                    
            


    def on_normal_message(self, eventobj: Event):
        """saves the message(or sends to application layer(sending to application layer is not implemented its just for explaining))
        decreases received message count
        works up the tree
        """

        pass
    
    def on_OK_message(self, neighboor):
        """
        decreases received OK message count
        works up the tree
        """
        self.adjok[neighboor] = True
        self.nonOK_count -= 1
    
    def round_end_check(self):
        """Only works in root node
        checks if all ok and all messages are received
        if so broadcasts new round
        """
        if not self.unreceived_count and not self.nonOK_count:
            if self.root:
                self.broadcast_go()
                self.new_round_event()
            else:
                for neighboor in self.adjnd:
                    self.send_message_event( 
                        EventTypes.MFRT,
                        neighboor,
                        f'OK#{self.round}',
                        nexthop=float('inf'),
                    )   
    
    def broadcast_go(self,round):
        """sharing broadcast to next nodes"""
        for neighboor in self.adjnd:
            self.send_message_event( 
                EventTypes.MFRT,
                neighboor,
                f'GO#{self.round}',
                nexthop=float('inf'),
            )              
