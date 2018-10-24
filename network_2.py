'''
Created on Oct 12, 2016

@author: mwittie
'''
import queue
import threading


## wrapper class for a queue of packets


class Interface:
    done_with_segmenting = False
    packet = ''

    ## @param maxsize - the maximum size of the queue storing packets
    def get_done_with_segmenting(self):
        return self.done_with_segmenting
    def set_done_with_segment(self, is_done):
        self.done_with_segmenting = is_done

    def __init__(self, maxsize=0):

        self.queue = queue.Queue(maxsize)
        self.mtu = None

    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None

    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception

    def put(self, pkt, block=False):
        self.queue.put(pkt, block)


## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths 
    dst_addr_S_length = 5

    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S):
        self.dst_addr = dst_addr
        self.data_S = data_S

    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()

    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return byte_S

    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0: NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length:]
        return self(dst_addr, data_S)


## Implements a network host for receiving and transmitting data
class Host:

    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False  # for thread termination

    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)

    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):
        p = NetworkPacket(dst_addr, data_S)

        # p1 = NetworkPacket(dst_addr, data_S[: 24])
        # p2 = NetworkPacket(dst_addr, data_S[24: len(p.data_S) + 1])
        # self.out_intf_L[0].put(p1.to_byte_S()) #send packets always enqueued successfully
        # print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p1, self.out_intf_L[0].mtu))
        # self.out_intf_L[0].put(p2.to_byte_S()) #send packets always enqueued successfully
        # print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p2, self.out_intf_L[0].mtu))
        self.in_intf_L[0].set_done_with_segment(True)
        self.out_intf_L[0].put(p.to_byte_S(), False)  # send packets always enqueued successfully
        self.in_intf_L[0].set_done_with_segment(False)

        print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

    ## receive packet from the network layer
    packet = ''
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        #self.packet += pkt_S
        if self.packet is not None and self.in_intf_L[0].get_done_with_segmenting():
            print('%s: received packet "%s" on the in interface' % (self, pkt_S))

    # def udt_receive(self, list):
    #     l = []
    #     l = list
    #
    #     pkt_S = self.in_intf_L[0].get()
    #     if pkt_S is not None:
    #         print('%s: received packet "%s" on the in interface' % (self, pkt_S))
    #         if l is None:
    #             l = [pkt_S]
    #             return l
    #         else:
    #             # return pkt_S
    #             l.append(pkt_S)
    #             return l

    ## thread target for the host to keep receiving data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            # receive data arriving to the in interface
            self.udt_receive()
            # terminate
            if (self.stop):
                print(threading.currentThread().getName() + ': Ending')
                return
        # print(threading.currentThread().getName() + ': Starting')
        # list = []
        # while True:
        #     # receive data arriving to the in interface
        #     list = self.udt_receive(list)
        #     # list.append(p)
        #     if list is not None:
        #         print("LIST: ", list[0: len(list) - 1])
        #     # print("STRING: ", string)
        #     # terminate
        #     if (self.stop):
        #         print(threading.currentThread().getName() + ': Ending')
        #         return


## Implements a multi-interface router described in class
class Router:

    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces 
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False  # for thread termination
        self.name = name
        # create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        i = 0
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            packet_array = []
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.from_byte_S(pkt_S) #parse a packet ou
                    ##TODO need to combine packets at host
                    # inputs the first 30 bytes into the interface

                    self.out_intf_L[i].put(p.to_byte_S()[0:30], True)
                    self.in_intf_L[i].set_done_with_segment(False)
                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                        % (self, p, i, i, self.out_intf_L[i].mtu))
                    # inputs the followint bits up to 60
                    self.out_intf_L[i].put(p.to_byte_S()[30:60], True)
                    self.in_intf_L[i].set_done_with_segment(True)
                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                          % (self, p, i, i, self.out_intf_L[i].mtu))

            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass


    ## thread target for the host to keep forwarding data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return
