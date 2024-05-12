import logging

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes

logger = logging.getLogger("AHC")


class ApplicationComponent(GenericModel):
    def __init__(self, component_name, component_id, topology=None):
        super(ApplicationComponent, self).__init__(component_name, component_id)
        self.topology = topology

    def find_total_node_number(self) -> int:
        return len(self.topology.nodes)

    def send_data(self, dst):
        payload = f"Data send by {self.componentname}-{str(self.componentinstancenumber)}"

        event = Event(self, EventTypes.MFRT, (dst, payload))
        self.send_down(event)

    def on_init(self, eventobj: Event):
        if self.componentinstancenumber == 0:
            last_components_id = self.find_total_node_number() - 1
            dst = last_components_id
            self.send_data(dst)

    def process_message(self, data: str) -> None:
        logger.info(f"I am {self.componentname}-{self.componentinstancenumber}, data received = {data}\n")

    def on_message_from_bottom(self, eventobj: Event):
        data = eventobj.eventcontent
        self.process_message(data)
