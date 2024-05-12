import logging
from copy import deepcopy
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, GenericMessage, GenericMessageHeader, ConnectorTypes
from ApplicationComponent import ApplicationComponent
from DSRAlgorithmComponent import DSRAlgorithmComponent
from DSRAlgorithmComponent import DSRMessageTypes
logger = logging.getLogger("AHC")


class AdhocNodeComponent(GenericModel):
    def __init__(self, component_name, component_id, topology=None):
        super(AdhocNodeComponent, self).__init__(component_name, component_id)
        self.Application = ApplicationComponent(ApplicationComponent.__name__, component_id, topology=topology)
        self.DSRAlgorithmComponent = DSRAlgorithmComponent(DSRAlgorithmComponent.__name__, component_id)

        self.Application.D(self.DSRAlgorithmComponent)
        self.DSRAlgorithmComponent.U(self.Application)

        self.DSRAlgorithmComponent.D(self)
        self.U(self.DSRAlgorithmComponent)

    def on_init(self, eventobj: Event):
        self.send_up(eventobj)

    def send_unicast_message(self, next_hop, payload):
        src = self.componentinstancenumber
        dst = next_hop
        header = GenericMessageHeader("", src, dst, nexthop=next_hop, interfaceid=f"{src}-{dst}")

        message = GenericMessage(header, payload)

        event = Event(self, EventTypes.MFRT, message)
        self.send_down(event)

    def send_broadcast_message(self, payload):
        for interface in self.connectors[ConnectorTypes.DOWN]:
            for next_hop in map(int, interface.componentinstancenumber.split("-")):
                if next_hop != self.get_component_id():
                    self.send_unicast_message(next_hop, payload)

    def send_message(self, next_hop, payload):

        if str("inf") == next_hop:
            self.send_broadcast_message(payload)
        else:
            self.send_unicast_message(next_hop, payload)

    def get_next_component_id(self, route: list):
        try:
            index_of_current_component = route.index(self.get_component_id())
            index_of_next_component = index_of_current_component + 1
            return route[index_of_next_component]
        except ValueError:
            print("[AdhocNodeComponent:get_next_component_id][Exception] ValueError")
            print("[AdhocNodeComponent:get_next_component_id][Exception] comp_id = " + str(self.get_component_id()))
            str_route = ' '.join(map(str, route))
            print("[AdhocNodeComponent:get_next_component_id][Exception] route = " + str_route)
            return None

    def get_prev_component_id(self, route: list):
        try:
            index_of_current_component = route.index(self.get_component_id())
            index_of_prev_component = index_of_current_component - 1
            return route[index_of_prev_component]
        except ValueError:
            print("[AdhocNodeComponent:get_prev_component_id][Exception] ValueError")
            print("[AdhocNodeComponent:get_prev_component_id][Exception] comp_id = " + str(self.get_component_id()))
            str_route = ' '.join(map(str, route))
            print("[AdhocNodeComponent:get_prev_component_id][Exception] route = " + str_route)
            return None

    def get_component_id(self) -> int:
        return self.componentinstancenumber

    def on_message_from_bottom(self, eventobj: Event):
        if eventobj.eventcontent.header.nexthop != self.get_component_id():
            return
        message_payload = eventobj.eventcontent.payload
        event = Event(self, EventTypes.MFRB, message_payload)
        logger.debug(f'I am: {self.get_component_id()}, event: {eventobj.eventcontent}')
        self.send_up(event)

    def is_link_up(self, next_hop) -> bool:
        for interface in self.connectors[ConnectorTypes.DOWN]:
            if interface.componentinstancenumber.split("-")[0] == str(self.componentinstancenumber):
                interface_next_hop = interface.componentinstancenumber.split("-")[1]
                if interface_next_hop == str(next_hop):
                    return True
            else:
                interface_next_hop = interface.componentinstancenumber.split("-")[0]
                if interface_next_hop == str(next_hop):
                    return True

        return False

    def on_message_from_top(self, eventobj: Event):
        src = eventobj.eventcontent.header.messagefrom

        message_type = eventobj.eventcontent.header.messagetype
        route = deepcopy(eventobj.eventcontent.header.route)

        next_hop = None
        if DSRMessageTypes.ROUTE_REQUEST == message_type:
            next_hop = str("inf")
        elif DSRMessageTypes.ROUTE_REPLY == message_type:
            next_hop = self.get_prev_component_id(route)
        elif DSRMessageTypes.ROUTE_ERROR == message_type:
            next_hop = self.get_prev_component_id(route)
        elif DSRMessageTypes.ROUTE_FORWARDING == message_type:
            next_hop = self.get_next_component_id(route)

        if next_hop is not None:
            self.send_message(next_hop, eventobj.eventcontent)

        if DSRMessageTypes.ROUTE_FORWARDING == message_type:
            if not self.is_link_up(next_hop):
                self.start_route_error_message(src, next_hop, route)

    def start_route_error_message(self, src, next_hop, route):

        try:
            new_src = self.get_component_id()
            new_dst = src

            header = GenericMessageHeader(DSRMessageTypes.ROUTE_ERROR, new_src, new_dst)

            index_of_current_component = route.index(self.get_component_id())
            new_route = route[0: index_of_current_component]

            broken_link = [self.get_component_id(), next_hop]

            event = Event(self,
                          EventTypes.MFRB,
                          GenericMessage(header,
                                         [new_route, broken_link]))

            self.send_up(event)

        except ValueError:
            print("[AdhocNodeComponent:send_route_error][Error] component_id not in the route")
            print("[AdhocNodeComponent:send_route_error][Error] comp_id = " + str(self.get_component_id()))
            str_route = ' '.join(map(str, route))
            print("[AdhocNodeComponent:send_route_error][Error] route = " + str_route)
