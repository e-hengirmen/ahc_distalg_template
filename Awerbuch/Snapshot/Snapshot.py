"""
Distributed Snapshot Algorithms

This module implemenTAKESNAPSHOT Chandy Lamport and Lai Yang algorithms.
"""


from enum import Enum
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from adhoccomputing.Generics import *
from collections import defaultdict

class SnapshotEventTypes(Enum):
    """ 
    Take snapshot event
    """ 
    TAKESNAPSHOT = "TAKESNAPSHOT"

class SnapshotMessageTypes(Enum):
    GLOBALSNAPSHOT = "GLOBALSNAPSHOT"


class SnapshotComponentModel(GenericModel):
    """
    A generic snapshot component model to implement various snapshot algorithms.

    Extend SnapshotComponentModel to implement your own snapshot algorithm.
    """
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        """
        Initializes the SnapshotComponentModel
        """
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.state = None
        self.gsu_redirected_comps = set()
        self.recv_events = []
        self.chnls = set()
        self.init_snapshot = False
        self.eventhandlers[SnapshotEventTypes.TAKESNAPSHOT] = self.take_snapshot

    def on_connected_to_component(self, name, channel):
        """
        on_connected_to_component is an event to address the channels
        """
        super().on_connected_to_component(name, channel)
        self.chnls.add(channel.componentinstancenumber)

    def channel_of(self, eventobj: Event):
        from_chnl = eventobj.fromchannel
        if from_chnl is None:
            raise Exception(f"Received a message from a non-channel component")

        return from_chnl

    def on_pre_event(self, event):
        """
        PreEvent Handler
        """
        return self.recv_events.append(event)


    def send_msg(self, event: Event):
        """Generic send message function"""
        pass
    
    def msg_recv(self, event: Event):
        """Generic message received function"""
        pass

    def send_gsu(self, local_state):
        """Send GLOBALSNAPSHOT message """
        gsu_msg = GenericMessage(
            GenericMessageHeader(SnapshotMessageTypes.GLOBALSNAPSHOT, None, None),
            local_state)
        self.send_msg(Event(self, EventTypes.MFRT, gsu_msg))

    def gsu_recv(self, state):
        # Redirect the GLOBALSNAPSHOT if we are not the source component of the snapshot
        if state.component_id not in self.gsu_redirected_comps:
            self.gsu_redirected_comps.add(state.component_id)
            self.send_gsu(state)

        self.on_gsu_recv(state)

    def on_gsu_recv(self, state):
        pass

    def on_take_snapshot(self):
        """Generic report snapshot"""
        pass

    def take_snapshot(self, eventobj: Event):
        self.init_snapshot = True
        self.on_take_snapshot()

    # When overridden call this function with 'super'
    def on_message_from_bottom(self, eventobj: Event):
        return self.msg_recv(eventobj)

    # When overridden call this function with 'super'
    def on_message_from_peer(self, eventobj: Event):
        return self.msg_recv(eventobj)

    # When overridden call this function with 'super'
    def on_message_from_top(self, eventobj: Event):
        return self.msg_recv(eventobj)

    def reset_state(self):
        self.state = None
        self.gsu_redirected_comps.clear()
