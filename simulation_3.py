'''
Created on Oct 12, 2016

@author: mwittie
'''

# modified by Keely Wiesbeck and Alex Harry
import network_3
import link_3
import threading
from time import sleep

##configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 10  # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads

    # create network nodes

    host_1 = network_3.Host(1)
    object_L.append(host_1)
    host_2 = network_3.Host(2)
    object_L.append(host_2)
    # in router forward {i is the in interface, x is the out interface} what i will determine where to route to
    # created routing tables, pass into the routers
    # 0 (host 1)is the first in interface passes to out interface 0 (Router B)
    # {host to end/or start at: out interface}
    routing_table_a = {3: 0, 4: 1, 0: 0, 1: 1}
    router_a = network_3.Router(routing_table_a, name='A', intf_count=2, max_queue_size=router_queue_size)
    object_L.append(router_a)
    routing_table_b = {3: 0, 4: 0}
    router_b = network_3.Router(routing_table_b, name='B', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_b)
    routing_table_c = {3: 0, 4: 0}
    router_c = network_3.Router(routing_table_c, name='C', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_c)
    routing_table_d = {3: 0, 4: 1}
    router_d = network_3.Router(routing_table_d, name='D', intf_count=2, max_queue_size=router_queue_size)
    object_L.append(router_d)
    host_3 = network_3.Host(3)
    object_L.append(host_3)
    host_4 = network_3.Host(4)
    object_L.append(host_4)

    # create a Link Layer to keep track of links between network nodes
    link_layer = link_3.LinkLayer()
    object_L.append(link_layer)

    # add all the links
    # link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    # out interface of client, in interface of server
    # 50 is the MTU - largest size of packet that can be transferred over links
    link_layer.add_link(link_3.Link(host_1, 0, router_a, 0, 50))
    link_layer.add_link(link_3.Link(host_2, 0, router_a, 1, 50))
    link_layer.add_link(link_3.Link(router_a, 0, router_b, 0, 50))
    link_layer.add_link(link_3.Link(router_a, 1, router_c, 0, 50))
    link_layer.add_link(link_3.Link(router_b, 0, router_d, 0, 50))
    link_layer.add_link(link_3.Link(router_c, 0, router_d, 1, 50))
    link_layer.add_link(link_3.Link(router_d, 0, host_3, 0, 50))
    link_layer.add_link(link_3.Link(router_d, 1, host_4, 0, 50))

    # start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=host_1.__str__(), target=host_1.run))
    thread_L.append(threading.Thread(name=host_2.__str__(), target=host_2.run))
    thread_L.append(threading.Thread(name=host_3.__str__(), target=host_3.run))
    thread_L.append(threading.Thread(name=host_4.__str__(), target=host_4.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))

    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()

    # create some send events
    # host 1 to host 3
    # host 2 to host 4
    for i in range(3):
        message = 'this is data message %d' % i
        # if statement to change which host to send to (host 3 or host 4)
        if i == 0 or i == 2:
            host_1.udt_send(3, message)
            print("Destination host: 3")
        else:
            host_2.udt_send(4, message)
            print("Destination host: 4")

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")

# writes to host periodically
