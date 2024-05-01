import queue
from enum import Enum

from adhoccomputing import GenericModel
from adhoccomputing.GenericModel import EventTypes
.Ahc import ComponentModel, Event

from ahc.Ahc import ComponentRegistry
from ahc.Ahc import GenericMessagePayload, GenericMessageHeader, GenericMessage, EventTypes
from ahc.Ahc import Topology

class IEEElectionComponent:
    def __init__(self, componentname, componentinstancenumber, num_worker_threads=1):
        self.eventhandlers = {}
        # If a component overwrites the __init__ method it has to call
        self.eventhandlers[EventTypes.INIT] = self.onInit
        self.eventhandlers[EventTypes.MFRB] = self.onMessageFromBottom
        self.eventhandlers[EventTypes.MFRT] = self.onMessageFromTop
        self.eventhandlers[EventTypes.MFRP] = self.onMessageFromPeer
        self.inputqueue = queue.Queue()
        self.componentname = componentname
        self.componentinstancenumber = componentinstancenumber
        self.num_worker_threads = num_worker_threads
        try:
            if self.connectors:
                pass
        except AttributeError:
            self.connectors = ConnectorList()
        
        self.registry = c()
        self.registry.addComponent(self)
        
        for i in range(self.num_worker_threads):
        t = Thread(target=self.queuehandler, args=[self.inputqueue])
        t.daemon = True
        t.start()