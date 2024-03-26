
from enum import Enum
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from adhoccomputing.Generics import *
from collections import defaultdict
from Snapshot.Snapshot import SnapshotComponentModel, SnapshotMessageTypes, SnapshotEventTypes


class LaiYangState:
    def __init__(self, comp_id, comp_state, received, sent):
        self.component_id = comp_id
        self.component_state = []
        for cs in comp_state:
            self.component_state.append(cs)

        self.received = defaultdict(list)
        for chnl, r in received.items():
            self.received[chnl].append(r)

        self.sent = defaultdict(list)
        for chnl, s in sent.items():
            self.sent[chnl].append(s)

class LaiYangComponentModel(SnapshotComponentModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.chnl_recv = defaultdict(list)
        self.chnl_sent = defaultdict(list)
        self.global_state = dict()
        self.sent_remaining = dict()
        self.recv_remaining = dict()

    def send_msg(self, event: Event):
        event.eventcontent = (event.eventcontent, self.state is not None)
        for c in self.chnls:
            self.chnl_sent[c].append(event)

        self.send_down(event)

    def handle_snapshot(self):
        # Take a snapshot
        self.state = LaiYangState(self.componentinstancenumber,
                                  self.recv_events, self.chnl_recv,
                                  self.chnl_sent)
        self.gsu_recv(self.state)

    def on_take_snapshot(self):
        self.handle_snapshot()

        # Broadcast a dummy message so that other components record
        # and broadcast their snapshots
        self.send_msg(Event(self, EventTypes.MFRT, "dummy"))

    def report_and_save_channel_state(self, channel, set_recv, set_sent):
        if not set_recv.issubset(set_sent):
            raise Exception("Not a consistent global state")

        chnl_state = list(set_sent - set_recv)
        self.global_state[channel] = chnl_state
        logger.debug(f"State of channel: {channel}=chnl_state")

    def on_gsu_recv(self, state: LaiYangState):
        if not self.init_snapshot:
            return
        # Report the snapshot if we are the source component of the snapshot
        self.global_state[state.component_id] = state.component_state
        report = f"State of component: {state.component_id}="
        report += ", ".join(str(e) for e in state.component_state)
        logger.debug(report)

        # Compute the messages in transit
        for chnl, recv in state.received:
            if chnl in self.sent_remaining:
                self.report_and_save_channel_state(
                    chnl, set(recv), set(self.sent_remaining[chnl]))
            else:
                self.recv_remaining[chnl] = recv

        for chnl, sent in state.sent:
            if chnl in self.recv_remaining:
                self.report_and_save_channel_state(
                    chnl, set(self.recv_remaining[chnl]), set(sent))
            else:
                self.sent_remaining[chnl] = sent

    def msg_recv(self, event: Event):
        content = event.eventcontent
        if type(content) is not tuple or len(content) != 2:
            raise Exception("Malformed message received by: "
                            "{self.unique_name()}")

        # Unpack the event content and modify the event with the actual content
        act_cntnt, post_snapshot = content
        event.eventcontent = act_cntnt

        # We are white and the message is post-snapshot
        if self.state is None and post_snapshot:
            self.handle_snapshot()

        from_chnl = self.channel_of(event)
        self.chnl_recv[from_chnl].append(event)

        # If not a GLOBALSNAPSHOT message return the modified event
        if type(act_cntnt) != GenericMessage or\
           type(header := act_cntnt.header) != GenericMessageHeader or\
               header.messagetype != SnapshotMessageTypes.GLOBALSNAPSHOT:
            return event

        self.gsu_recv(act_cntnt.payload)
        return event

    def reset_state(self):
        super().reset_state()
        self.global_state.clear()