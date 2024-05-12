"""
IEEE-1394 election implementation
"""

from time import time
import queue
import logging
from time import sleep

from enum import Enum

from adhoccomputing.GenericModel import EventTypes, GenericModel, Event
from adhoccomputing.Generics import ConnectorList, ConnectorTypes
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

import threading

from BaseComponent import BaseComponent

logger = logging.getLogger("AHC")


class ThreadSafeSet:
    """A thread-safe set implementation using a mutex.(not used)
    """

    def __init__(self, tmplist = [], lock=None):
        self._set = set(tmplist)
        self._lock = lock
        if lock is None:
            self._lock = threading.Lock()

    def add(self, item):
        with self._lock:
            self._set.add(item)

    def remove(self, item):
        with self._lock:
            try:
                self._set.remove(item)
            except:
                pass

    def contains(self, item):
        with self._lock:
            return item in self._set

    def pop(self):
        with self._lock:
            if not self._set:
                raise KeyError("pop from an empty set")
            item = self._set.pop()
        return item
    
    def len(self):
        with self._lock:
            return len(self._set)










# class IEEE1394_EventTypes(Enum):
#     """corresponding naming:
#     BE_MY_FATHER_ANAKIN: parent request
#     I_AM_YOUR_FATHER_LUKE: acknowledgement
#     CHOOSING_FATHER: root contention (realized with my version its not needed)

#     Args:
#         Enum (_type_): _description_
#     """

#     BE_MY_FATHER_ANAKIN = "BE_MY_FATHER_ANAKIN"
#     I_AM_YOUR_FATHER_LUKE = "I_AM_YOUR_FATHER_LUKE"
#     # CHOOSING_FATHER = "CHOOSING_FATHER" 

# def IEEE1394_Channel_EventTypes(Enum):
#     pass


class ChannelComponentModel(GenericChannel):
    """Channel component model to send to only 1 peer
    """
    def on_init(self, eventobj: Event):
        # print(f'\n\n\nCONNECTORS are:{[(i.componentname, i.componentinstancenumber) for i in self.connectors[ConnectorTypes.PEER]]}\n\n\n')
        pass
        
    # def on_message_from_peer(self, eventobj: Event):
    #     messagefrom = eventobj.eventcontent.header.messagefrom
    #     messageto = eventobj.eventcontent.header.messageto
    #     # print(f'channel received: {messagefrom} -> {messageto}')
    #     logger.debug(f"{self.componentname}-{self.componentinstancenumber} on_deliver_to_component {self.componentname}")
    #     myevent = Event(self, EventTypes.MFRB,
    #                     eventobj.eventcontent, fromchannel=self.componentinstancenumber,
    #                     eventid=eventobj.eventid, eventsource_componentname=eventobj.eventsource_componentname, eventsource_componentinstancenumber=eventobj.eventsource_componentinstancenumber)
    #     myevent.eventsource=None
    #     self.send_up_from_channel(myevent, loopback=False)

    # def on_message_from_top(self, eventobj: Event):
    #     eventobj.event = EventTypes.MFRP
    #     eventobj.fromchannel = self.componentinstancenumber
    #     self.send_to_specific_peer(eventobj)

        # self.eventhandlers[IEEE1394_EventTypes.BE_MY_FATHER_ANAKIN] = self.parentage_request
        # self.eventhandlers[IEEE1394_EventTypes.I_AM_YOUR_FATHER_LUKE] = self.father_acknowledgement
        # logger.debug(f"connectors: {self.componentinstancenumber,self.componentname} {[p.componentinstancenumber for p in self.connectors[ConnectorTypes.PEER]]}")
    # def parentage_request(self, eventobj: Event):
    #     eventobj.event = EventTypes.MFRP
    #     eventobj.fromchannel = self.componentinstancenumber
    #     self.send_peer(eventobj)
    
    # def father_acknowledgement(self, eventobj: Event):
    #     eventobj.event = EventTypes.MFRP
    #     eventobj.fromchannel = self.componentinstancenumber
    #     self.send_peer(eventobj)

    # def on_message_from_peer(self, eventobj: Event):
    #     logger.debug(f"{self.componentname}-{self.componentinstancenumber} on_deliver_to_component {self.componentname}")
    #     myevent = Event(self, EventTypes.MFRB,
    #                     eventobj.eventcontent, fromchannel=self.componentinstancenumber,
    #                     eventid=eventobj.eventid, eventsource_componentname=eventobj.eventsource_componentname, eventsource_componentinstancenumber=eventobj.eventsource_componentinstancenumber)
    #     myevent.eventsource=None
    #     self.send_up_from_channel(myevent, loopback=False)


class AlgorithmComponent(BaseComponent):
    end_time = -1
    def on_init(self, eventobj: Event):
        """On init function that initiates neccessary lock and variables
        also calls u_are_my_father_anakin(for those who only has one neighboor left marks them as their parent 

        Args:
            eventobj (Event): _description_
        """
        super().on_init(eventobj)
        self.neighbour_set = set(self.topology.get_neighbors(self.componentinstancenumber))
        self.lock = threading.Lock()
        # self.can_be_parent_set = ThreadSafeSet(self.topology.get_neighbors(self.componentinstancenumber) ,lock=self.lock)
        self.can_be_parent_set = set(self.topology.get_neighbors(self.componentinstancenumber))

        # self.eventhandlers[IEEE1394_EventTypes.BE_MY_FATHER_ANAKIN] = self.am_i_ready_to_be_a_father
        # self.eventhandlers[IEEE1394_EventTypes.I_AM_YOUR_FATHER_LUKE] = self.he_was_my_father

        self.parent = None
        self.leader = False
        self.ended = False

        self.u_are_my_father_anakin()

        # self.debug_message("neighboor_list" + str(self.neighbour_set))

    def u_are_my_father_anakin(self):
        """Sends a parent request to the only neighbour node(lets call that node Anakin).
        There can be multiple neighboors but this is the only node that hasn't sent a parent request to our node.
        """
        # self.debug_message('before entering lock 1')
        with self.lock:
            if len(self.can_be_parent_set) == 1:
                father_to_be = self.can_be_parent_set.pop()
                self.can_be_parent_set.add(father_to_be)
                # self.parent = father_to_be
                if father_to_be > self.componentinstancenumber:
                    self.parent = father_to_be
                    self.can_be_parent_set.pop()
                # self.debug_message(f"Be my father {father_to_be} {self.can_be_parent_set}")
                self.debug_message(f"Be my father {father_to_be}")
                self.send_message_event(
                    EventTypes.MFRT,
                    father_to_be,
                    "Father?",
                    # nexthop=father_to_be,
                )
        # self.debug_message('exited lock 1')
            
    def on_message_from_bottom(self, eventobj: Event):
        """ By looking at the message (looking for parent request or acknowledgement calls the neccessary function)

        Args:
            eventobj (Event): _description_

        Raises:
            Exception: _description_
        """
        super().on_message_from_bottom(eventobj)
        if self.componentinstancenumber == eventobj.eventcontent.header.messageto:
            self.debug_message(f"RECEIVED from {eventobj.eventsource_componentinstancenumber}: {eventobj.eventcontent.payload.messagepayload}")
            if eventobj.eventcontent.payload.messagepayload == "Father?":
                self.am_i_ready_to_be_a_father(eventobj)
            elif eventobj.eventcontent.payload.messagepayload == "ACKNOWLEDGEMENT_RECEIVED":
                self.he_was_my_father(eventobj)
            else:
                raise Exception(f"content '{eventobj.eventcontent.payload.messagepayload}' was sent")
    
    def am_i_ready_to_be_a_father(self, eventobj: Event):
        """Sends ACK if there is no contention.
        Otherwise sends ack if having higher id
        Otherwise sends father request instead forcing the other party to be the fater

        Args:
            eventobj (Event): _description_
        """
        # self.debug_message('before entering lock 2')
        with self.lock:
            neighboor = eventobj.eventsource_componentinstancenumber
            message = None
            self.debug_message(f'parent: {self.parent}')
            if self.parent and self.parent == neighboor:
                message = "Father?" 
            elif not (neighboor in self.can_be_parent_set):
                message = "ACKNOWLEDGEMENT_RECEIVED"
            elif len(self.can_be_parent_set) > 1:
                self.can_be_parent_set.remove(neighboor)
                message = "ACKNOWLEDGEMENT_RECEIVED"
            elif len(self.can_be_parent_set) == 1:     # root contention 
                if self.componentinstancenumber > neighboor:
                    # print('here4', self.componentinstancenumber)
                    self.can_be_parent_set.remove(neighboor)
                    message = "ACKNOWLEDGEMENT_RECEIVED"
                    self.leader = True
                else:
                    message = "Father?"
        # self.debug_message('exited lock 2')
        
        if message == "Father?":
            self.u_are_my_father_anakin()
        elif message == "ACKNOWLEDGEMENT_RECEIVED":
            self.debug_message(f"I wanna be your father {neighboor}")
            self.send_message_event(
                EventTypes.MFRT,
                neighboor,
                "ACKNOWLEDGEMENT_RECEIVED",
                # nexthop=neighboor,
            )
        if self.leader == True:
            print(f"(election over) Anakin's gone I am what remains {self.componentinstancenumber}")
            AlgorithmComponent.end_time = time()

        elif message == "ACKNOWLEDGEMENT_RECEIVED":
            self.u_are_my_father_anakin()

    def he_was_my_father(self, eventobj: Event):
        """Marking acked node as father

        Args:
            eventobj (Event): _description_

        Raises:
            Exception: _description_
        """
        neighboor = eventobj.eventsource_componentinstancenumber
        if self.parent and self.parent != eventobj.eventsource_componentinstancenumber:
            raise Exception("multiple parent error")
        self.parent = eventobj.eventsource_componentinstancenumber
        # self.debug_message('before entering lock 3')
        with self.lock:
            if not self.ended:
                try:
                    self.can_be_parent_set.pop()
                except:
                    pass
                self.ended = True
        # self.debug_message('exited lock 3')
        self.debug_message(f"{neighboor} is my father {self.can_be_parent_set}")

    


