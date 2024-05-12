.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I implemented IEEE 1394 election algorithm on the AHCv2 platform. The specific
details of the implementation can be seen through the documentation part and githubpage, including data structures,
message formats.

For the data we tested with:

- A small(3 node line) graph
- Medium sized random spanning trees(with different largest branch sizes)
- A large sized spanning trees 

Results
~~~~~~~~

The leader election process seems to scale linearly with the number of nodes there was no important scaling related to largest branch size in our simulation.

Discussion
~~~~~~~~~~

As said in results: The leader election process seems to scale linearly with the number of nodes.
In my opinion it should have scaled linearly with the length of the largest branch.
It's possible that the AHCv2 simulation environment introduces limitations that affect the scalability. If the simulation runs sequentially or utilizes a limited number of cores, it might not accurately capture the parallel nature of message passing in a real IEEE 1394 network. In a real network, nodes can potentially communicate with their neighbors simultaneously, leading to faster leader election even with a large number of nodes.
