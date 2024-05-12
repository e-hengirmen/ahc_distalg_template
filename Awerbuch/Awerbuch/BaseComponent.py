"""A base class to be used for our nodes later on with additional features of easier logging and message sending ease.
"""
import queue
import logging

from enum import Enum

from adhoccomputing.GenericModel import EventTypes, GenericModel, Event
from adhoccomputing.Generics import ConnectorList, ConnectorTypes, GenericMessage, GenericMessageHeader, GenericMessagePayload

from threading import Thread
logger = logging.getLogger("AHC")


class BaseComponent(GenericModel):
    """A base class to be used for our nodes later on with additional features of easier logging and message sending ease.
    """

    msg_count = 0
    def __init__(self, component_name, componentinstancenumber, topology=None):
        super().__init__(component_name, componentinstancenumber, topology=topology)
        self.component_hash = self.componentname, self.componentinstancenumber

    def on_init(self, eventobj: Event):
        self.debug_message(f"INIT - {self.component_hash}")

    def on_message_from_top(self, eventobj: Event):
        # self.debug_message(self.on_message_logger(eventobj, "FROM TOP:"))
        pass
    
    def on_message_from_bottom(self, eventobj: Event):
        # self.debug_message(self.on_message_logger(eventobj, "FROM BOTTOM:"))
        pass

    def on_message_from_peer(self, eventobj: Event):
        # self.debug_message(self.on_message_logger(eventobj, "FROM PEER:"))
        pass
    
    def on_message_logger(self, eventobj: Event, pretext, add_content = False):
        msg = pretext + f" MSG FROM: {eventobj.eventsource_componentname,eventobj.eventsource_componentinstancenumber}"
        if add_content:
            msg += f", eventcontent:{eventobj.eventcontent}"
        msg += "\n"
        return msg
    
    def debug_message(self, msg):
        # if self.componentinstancenumber==1:
        #     print(str(self.component_hash) + ": " + str(msg))
        logger.info(str(self.component_hash) + ": " + str(msg))


    def create_message_event(
        self,
        messagetype,
        messageto,
        messagecontent,
        nexthop=float('inf'),
    ):
        message = GenericMessage(
            GenericMessageHeader(messagetype, messagefrom=self.componentinstancenumber, messageto=messageto, nexthop=nexthop),
            GenericMessagePayload(messagecontent),
        )
        event = Event(self, messagetype, message, eventsource_componentinstancenumber=self.componentinstancenumber)
        return event

    def send_message_event(
        self,
        messagetype,
        messageto,
        messagecontent,
        nexthop=float('inf'),
    ):
        event = self.create_message_event(
            messagetype,
            messageto,
            messagecontent,
            nexthop,
        )
        self.msg_count += 1
        self.debug_message(f"SENDING to {messageto}: {messagecontent}")
        self.send_down(event)
