import queue
import logging

from enum import Enum

from adhoccomputing.GenericModel import EventTypes, GenericModel, Event
from adhoccomputing.Generics import ConnectorList, ConnectorTypes

from threading import Thread

from BaseComponent import BaseComponentModel
from AlgorithmComponent import AlgorithmComponentModel 

logger = logging.getLogger("AHC")

class NodeComponentModel(BaseComponentModel):
    def __init__(self, component_name, componentinstancenumber, topology=None):
        
        super().__init__(component_name, componentinstancenumber, topology=topology)
        self.algorithm_component = AlgorithmComponentModel(AlgorithmComponentModel.__name__, componentinstancenumber, topology=topology)
        self.algorithm_component.connect_me_to_component(ConnectorTypes.DOWN, self)
        self.connect_me_to_component(ConnectorTypes.UP, self.algorithm_component)

    def on_init(self, eventobj: Event):
        super().on_init(eventobj)
        self.send_up(eventobj)

        # if not self.componentinstancenumber:
        #     self.send_message(
        #         EventTypes.MFRT,
        #         1,
        #         "ERSEL",
        #         nexthop=1,
                
        #     )

    

