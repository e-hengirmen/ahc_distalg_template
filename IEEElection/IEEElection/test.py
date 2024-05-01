import logging
from time import sleep

import matplotlib.pyplot as plt
import networkx as nx
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, setAHCLogLevel
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer
from adhoccomputing.Networking.ApplicationLayer.GenericApplicationLayer import GenericApplicationLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

from IEEElectionComponent import IEEElectionComponent

number_mesg = 0
topo = Topology()


class AdHocNode(GenericModel):

    def on_init(self, eventobj: Event):
        print(f"Initializing {self.componentname}.{self.componentinstancenumber}")

    def on_message_from_top(self, eventobj: Event):
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

    def on_message_from_bottom(self, eventobj: Event):
        self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))

    def __init__(self, componentname, componentid, topology=None):
        super().__init__(componentname, componentid, topology=topo)
        self.components = []
        # SUBCOMPONENTS
        self.appllayer = GenericApplicationLayer("ApplicationLayer", componentid, topology=topology)
        self.netlayer = GenericNetworkLayer("NetworkLayer", componentid, topology=topology)
        self.linklayer = GenericLinkLayer("LinkLayer", componentid)
        self.components.append(self.appllayer)
        self.components.append(self.netlayer)
        self.components.append(self.linklayer)

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.appllayer.D(self.netlayer)
        self.netlayer.U(self.appllayer)
        self.netlayer.D(self.linklayer)
        self.linklayer.U(self.netlayer)

        # Connect the bottom component to the composite component....
        self.linklayer.D(self)
        self.U(self.linklayer)


class Channel(GenericChannel):
    def on_init(self, eventobj: Event):
        pass


def main():
    G = nx.Graph()
    # for i in range(5):
    #     G.add_node(i)
    #
    # G.add_edge(0, 1)
    # G.add_edge(0, 3)
    # G.add_edge(0, 4)
    # G.add_edge(1, 2)
    # G.add_edge(1, 3)
    # G.add_edge(1, 4)
    # G.add_edge(2, 1)
    # G.add_edge(2, 4)
    # G.add_edge(2, 3)
    # G.add_edge(3, 1)
    # G.add_edge(3, 0)
    # G.add_edge(3, 2)

    G.add_node(0)
    G.add_node(1)
    G.add_node(2)
    G.add_edge(0, 1)
    G.add_edge(1, 2)

    # G = nx.random_geometric_graph(50, 0.5)
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.draw()

    print("Starting DSR test")
    # topo is defined as a global variable
    topo.construct_from_graph(G, IEEElectionComponent, Channel)
    setAHCLogLevel(logging.DEBUG)
    topo.start()

    # plt.show()
    sleep(0.15)


if __name__ == "__main__":
    main()