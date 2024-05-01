import queue
import logging

from enum import Enum

from adhoccomputing.GenericModel import EventTypes, GenericModel, Event
from adhoccomputing.Generics import ConnectorList, ConnectorTypes, GenericMessage, GenericMessageHeader, GenericMessagePayload

from threading import Thread
logger = logging.getLogger("AHC")


class BaseComponentModel(GenericModel):
    def __init__(self, component_name, componentinstancenumber, topology=None):
        super().__init__(component_name, componentinstancenumber, topology=topology)
        self.component_hash = self.componentname, self.componentinstancenumber

    def on_init(self, eventobj: Event):
        logger.debug(f"INIT - {self.component_hash}")
    
    def on_message_from_top(self, eventobj: Event):
        logger.debug(self.on_message_logger(eventobj, "FROM TOP:"))
    
    def on_message_from_bottom(self, eventobj: Event):
        logger.debug(self.on_message_logger(eventobj, "FROM BOTTOM:"))

    def on_message_from_peer(self, eventobj: Event):
        logger.debug(self.on_message_logger(eventobj, "FROM PEER:"))
    
    def on_message_logger(self, eventobj: Event, pretext, add_content = True):
        msg = pretext + f" {self.component_hash} <- {eventobj.eventsource_componentname,eventobj.eventsource_componentinstancenumber}"
        if add_content:
            msg += f", eventcontent={eventobj.eventcontent}"
        msg += "\n"
        return msg


    def create_message_event(
            self,
            messagetype,
            messageto,
            messagecontent,
            nexthop=float('inf'),
        ):
        message = GenericMessage(
            GenericMessageHeader(messagetype, self.componentinstancenumber, messageto, nexthop),
            GenericMessagePayload(messagecontent),
        )
        event = Event(self, EventTypes.MFRT, message)
        return event
