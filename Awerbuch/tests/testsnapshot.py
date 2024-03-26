#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.getcwd())

from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel

from Snapshot.ChandyLamportSnapshot import ChandyLamportComponentModel
from Snapshot.Snapshot import SnapshotEventTypes

# Wrap Snapshot in a node model!

def main():
    setAHCLogLevel(DEBUG)
    topo = Topology()
    # A larger topology is required for testing
    topo.construct_sender_receiver(ChandyLamportComponentModel,
                                   ChandyLamportComponentModel, GenericChannel)
    
    topo.start()
    time.sleep(1)
    topo.sender.send_self(Event(topo.sender, SnapshotEventTypes.TAKESNAPSHOT, None))
    time.sleep(5)
    topo.exit()
if __name__ == "__main__":
    exit(main())