.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I implemented Awerbuch's Alpha, Beta, and Gamma synchronization algorithms on the AHCv2 platform.
The specific details of the implementation can be seen through the documentation part and githubpage, including data structures, message formats.

For the data We have tested with:

- A small sized connected Graph
- A medium sized graph in the shape of a binary tree
- A big sized connected randomized graph

Results
~~~~~~~~

- Alpha: Alpha showed lower time usage due to its single-round message exchange per round. However, its message overall message count was higher compared to Beta and Gamma, especially in dense networks with high edge count (E).

- Beta: Beta's message count was comparable to Alpha's, but it took more time than others. This is because processes wait for acknowledgments from all children, potentially leading to longer waiting times in deeper parts of the tree.

- Gamma: Gamma aims to balance message and time complexity by utilizing Beta within trees and Alpha between trees. It had about the same amount of messages. However, time taken was between Alpha and Beta.

Discussion
~~~~~~~~~~

This paper presented an overview of Awerbuch's Alpha, Beta, and Gamma synchronization algorithms. We discussed their functionalities and key characteristics, including message complexity and time complexity.

- Alpha prioritizes speed
- Beta prioritizes global consistency
- Gamma seeks balance