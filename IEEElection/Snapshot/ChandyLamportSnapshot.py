"""
The Chandy-Lamport Algorithm is a key method for capturing consistent global snapshots in distributed systems, comprising the initiation of marker propagation, recording of local states by processes upon marker reception, and subsequent snapshot reconstruction. It allows for the capture of snapshots without halting system execution, facilitating concurrent operations and serving various purposes like debugging and failure recovery. However, the algorithm exhibits limitations including increased message overhead due to marker propagation, challenges in managing concurrency which may affect snapshot accuracy, potential difficulties in handling faults during snapshot collection, and scalability concerns as system size grows. Despite these limitations, the Chandy-Lamport Algorithm remains foundational in distributed systems, driving further research in snapshot capture techniques.
"""

from enum import Enum
from collections import defaultdict
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader,  GenericMessage
from adhoccomputing.Generics import *
from Snapshot.Snapshot import SnapshotComponentModel, SnapshotMessageTypes, SnapshotEventTypes



class ChandyLamportMessageTypes(Enum):
    MARKER = "MARKER"


class ChandyLamportState:
    """
    ChandyLamportState keeps track of states.
    """

    def __init__(self, component, state, chnl_states):
        self.component_id = component
        self.component_state = []
        for s in state:
            self.component_state.append(s)

        self.chnl_states = defaultdict(list)
        for c, s in chnl_states.items():
            self.chnl_states[c].append(s)

class ChandyLamportComponentModel(SnapshotComponentModel):
    """
    A ComponentModel that you can take a snapshot of using the Chandy-Lamport algorithm
    """

    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.global_state = dict()
        self.in_chnl_states = defaultdict(list)
        self.in_chnl_events = defaultdict(list)
        self.mark_recv_chnls = set()
        self.gsu_chnls = set()

    def on_gsu_recv(self, state: ChandyLamportState):
        if not self.init_snapshot:
            return

        report=f"State of component: {state.component_id}="
        report += ", ".join(str(e) for e in state.component_state)
        logger.debug(report)
        for chnl, events in state.chnl_states.items():
            chnl_rep = f"State of channel: {chnl}="
            chnl_rep += ", ".join(str(e) for e in events)
            logger.debug(chnl_rep)

    def send_msg(self, event: Event):
        self.send_down(event)

    def mark_send(self):
        # Record the state
        self.state = []
        for re in self.recv_events:
            self.state.append(re)

        # Broadcast the mark message
        mark_msg = GenericMessage(
            GenericMessageHeader(ChandyLamportMessageTypes.MARKER, None, None),
            None)
        self.send_msg(Event(self, EventTypes.MFRT, mark_msg))

    def on_take_snapshot(self):
        """Initializes a global snapshot and a report will be printed out when
        complete"""
        self.mark_send()

    def mark_recv(self, from_chnl):
        if self.state is None:
            # First mark message, save component and channel state
            self.mark_send()
            self.in_chnl_states[from_chnl] = []
        else:
            # Consequent mark messages, save channel states
            for e in self.in_chnl_events[from_chnl]:
                self.in_chnl_states[e].append(e)

        self.mark_recv_chnls.add(from_chnl)
        if self.mark_recv_chnls == self.chnls:
            # Local snapshot completed, broadcast the local state
            local_state = ChandyLamportState(self.componentinstancenumber,
                                             self.state, self.in_chnl_states)
            gsu_msg = GenericMessage(
                GenericMessageHeader(SnapshotMessageTypes.GLOBALSNAPSHOT, None, None),
                local_state)
            self.send_msg(Event(self, EventTypes.MFRT, gsu_msg))
            self.gsu_recv(local_state)

    def msg_recv(self, event: Event):
        from_chnl = self.channel_of(event)
        # If received message is of type MARKER or GLOBALSNAPSHOT; process them separately
        if type(contnt := event.eventcontent) == GenericMessage and\
           type(header := contnt.header) == GenericMessageHeader:
            if header.messagetype == ChandyLamportMessageTypes.MARKER:
                self.mark_recv(from_chnl)
            elif header.messagetype == SnapshotMessageTypes.GLOBALSNAPSHOT:
                self.gsu_recv(contnt.payload)

            return event

        if self.state is None:
            return event

        # If the state is not recorded
        if from_chnl not in self.in_chnl_states:
            self.in_chnl_events[from_chnl].append(event)

        return event

    def reset_state(self):
        super().reset_state()
        self.in_chnl_states.clear()
        self.in_chnl_events.clear()
        self.mark_recv_chnls.clear()

