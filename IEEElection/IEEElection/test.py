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

# from AlgorithmComponent import AlgorithmComponentModel
from NodeComponent import NodeComponentModel as NodeModel

number_mesg = 0
topo = Topology()



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

    print("Starting test")
    # topo is defined as a global variable
    topo.construct_from_graph(G, NodeModel, Channel)
    setAHCLogLevel(logging.DEBUG)
    topo.start()

    # plt.show()
    sleep(0.15)


if __name__ == "__main__":
    main()