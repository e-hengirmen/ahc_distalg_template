import queue
import logging
from time import sleep

from enum import Enum

from adhoccomputing.GenericModel import EventTypes, GenericModel, Event
from adhoccomputing.Generics import ConnectorList, ConnectorTypes
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

import threading

from BaseComponent import BaseComponentModel

logger = logging.getLogger("AHC")


class ThreadSafeSet:
    """A thread-safe set implementation using a mutex.
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
    def on_init(self, eventobj: Event):
        # print(f'\n\n\nCONNECTORS are:{[(i.componentname, i.componentinstancenumber) for i in self.connectors[ConnectorTypes.PEER]]}\n\n\n')
        pass
        
    def on_message_from_peer(self, eventobj: Event):
        messagefrom = eventobj.eventcontent.header.messagefrom
        messageto = eventobj.eventcontent.header.messageto
        # print(f'channel received: {messagefrom} -> {messageto}')
        logger.debug(f"{self.componentname}-{self.componentinstancenumber} on_deliver_to_component {self.componentname}")
        myevent = Event(self, EventTypes.MFRB,
                        eventobj.eventcontent, fromchannel=self.componentinstancenumber,
                        eventid=eventobj.eventid, eventsource_componentname=eventobj.eventsource_componentname, eventsource_componentinstancenumber=eventobj.eventsource_componentinstancenumber)
        myevent.eventsource=None
        self.send_up_from_channel(myevent, loopback=False)

    def on_message_from_top(self, eventobj: Event):
        eventobj.event = EventTypes.MFRP
        eventobj.fromchannel = self.componentinstancenumber
        self.send_to_specific_peer(eventobj)

    def send_to_specific_peer(self, event: Event):
        messagefrom = event.eventcontent.header.messagefrom
        messageto = event.eventcontent.header.messageto
        try:
            # counter = 0
            for p in self.connectors[ConnectorTypes.PEER]:
                if (
                    p.componentinstancenumber == f'{messagefrom}-{messageto}' or
                    p.componentinstancenumber == f'{messageto}-{messagefrom}'
                ):
                    # counter += 1
                    # print(f'channel sendto: {messagefrom} -> {messageto}, {p.componentinstancenumber}')
                    p.trigger_event(event)
            # print("\n\n\nsend to", counter, f'{messagefrom}-{messageto}', f'{messageto}-{messagefrom}\t{event.eventcontent.header}, {event.eventcontent.payload.messagepayload}',"\n\n\n")
        except Exception as e:
            logger.error(f"Cannot send message to PEER Connector {self.componentname}-{self.componentinstancenumber} {str(event)} {e}")
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


class AlgorithmComponentModel(BaseComponentModel):
    def on_init(self, eventobj: Event):
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
        self.debug_message('before sending u are my father')
        with self.lock:
            self.debug_message('sending u are my father')
            if len(self.can_be_parent_set) == 1:
                father_to_be = self.can_be_parent_set.pop()
                self.can_be_parent_set.add(father_to_be)
                # self.parent = father_to_be
                if father_to_be > self.componentinstancenumber:
                    self.parent = father_to_be

                self.debug_message(f"Be my father {father_to_be} {self.can_be_parent_set}")
                self.send_message_event(
                    EventTypes.MFRT,
                    father_to_be,
                    "Father?",
                    nexthop=father_to_be,
                )
            else:
                return
            
    def on_message_from_bottom(self, eventobj: Event):
        super().on_message_from_bottom(eventobj)
        self.debug_message(f"RECEIVED from {eventobj.eventsource_componentinstancenumber}: {eventobj.eventcontent.payload.messagepayload} {self.can_be_parent_set}")
        if eventobj.eventcontent.payload.messagepayload == "Father?":
            self.am_i_ready_to_be_a_father(eventobj)
        elif eventobj.eventcontent.payload.messagepayload == "ACK":
            self.he_was_my_father(eventobj)
        else:
            raise Exception(f"content '{eventobj.eventcontent.payload.messagepayload}' was sent")
    
    def am_i_ready_to_be_a_father(self, eventobj: Event):
        with self.lock:
            neighboor = eventobj.eventsource_componentinstancenumber
            message = None
            self.debug_message(f'parent: {self.parent}')
            if self.parent and self.parent == neighboor:
                message = "Father?" 
            elif not (neighboor in self.can_be_parent_set):
                message = "ACK"
            elif len(self.can_be_parent_set) > 1:
                self.can_be_parent_set.remove(neighboor)
                message = "ACK"
            elif len(self.can_be_parent_set) == 1:     # root contention 
                if self.componentinstancenumber > neighboor:
                    print('here4', self.componentinstancenumber)
                    self.can_be_parent_set.remove(neighboor)
                    message = "ACK"
                    self.leader = True
                else:
                    print('here5')
                    message = "Father?"
            if message == "Father?":
                self.u_are_my_father_anakin()
            elif message == "ACK":
                self.debug_message(f"I wanna be your father {neighboor} {self.can_be_parent_set}")
                self.send_message_event(
                    EventTypes.MFRT,
                    neighboor,
                    "ACK",
                    nexthop=neighboor,
                )
        if self.leader == True:
            print(f"(election over) Anakin's gone I am what remains {self.can_be_parent_set}")
        elif message == "ACK":
            self.u_are_my_father_anakin()

    def he_was_my_father(self, eventobj: Event):
        neighboor = eventobj.eventsource_componentinstancenumber
        self.parent = eventobj.eventsource_componentinstancenumber
        with self.lock:
            if not self.ended:
                try:
                    self.can_be_parent_set.pop()
                except:
                    pass
                self.ended = True
        self.debug_message(f"{neighboor} is my father {self.can_be_parent_set}")

    


