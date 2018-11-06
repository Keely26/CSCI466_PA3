'''
Created on Oct 12, 2016

@author: mwittie
'''
import math
import queue
import threading


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
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
    length_S_length = 5 # length of the packet
    if_segment = 1 # value to tell if packet is a segment
    if_last = 1 # flag to tell if segment is last segment of packet
    message_number = 1


    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S, if_segment, if_last, message_number):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.if_segment = if_segment
        self.if_last = if_last
        self.message_number = message_number

    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()

    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length - 3) # packet address
        # byte_s = if_segment + seg_flag + address + message
        byte_S = str(self.if_segment) + str(self.if_last) + str(self.message_number) + str(byte_S) + str(self.data_S)
        # byte_S += self.data_S
        return byte_S

    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[3 : NetworkPacket.dst_addr_S_length])
        # pack_length = int(byte_S[])
        if_last = (byte_S[1])
        if_seg = (byte_S[0])
        mes_num = byte_S[2]
        data_S = byte_S[NetworkPacket.dst_addr_S_length : ]
        # offset = int(byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.seg_flag_S_length
        # : NetworkPacket.dst_addr_S_length + NetworkPacket.seg_flag_S_length + NetworkPacket.offset_S_length])
        return self(dst_addr, data_S, if_seg, if_last, mes_num)


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
    def udt_send(self, dst_addr, data_S, mes_num):
        p = NetworkPacket(dst_addr, data_S, 0, 0, mes_num)
        #print("IN SEND")
        #print("MTU: ", self.out_intf_L[0].mtu)
        if len(data_S) > self.out_intf_L[0].mtu:
            messages = []
            mes = data_S
            cur = 0
            while (len(mes)>self.out_intf_L[0].mtu - 5):
                messages.append(''.join(mes[0:self.out_intf_L[0].mtu - 5])) # add split messages to array
                mes = mes[self.out_intf_L[0].mtu - 5:] # update message
            if len(mes) > 0:
                messages.append(mes)
            for j in messages: # for each message
                # print("CURRENT: ", cur)
                if cur == len(messages) - 1: # if current message is the last
                    packet = NetworkPacket(dst_addr, j, 1, 1, mes_num) # create packet with updated if_last variable
                    self.out_intf_L[0].put(packet.to_byte_S())
                    print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, packet, self.out_intf_L[0].mtu))
                else:
                    packet = NetworkPacket(dst_addr, j, 1, 0, mes_num) # create packet that is not last
                    cur += 1 # update number of current packet
                    self.out_intf_L[0].put(packet.to_byte_S())
                    print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, packet, self.out_intf_L[0].mtu))

        else:
            self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
            print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

    packets0 = []
    packets1 = []
    packets2 = []
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        message0 = ''
        message1 = ''
        message2 = ''
        if pkt_S is not None:
            #print('%s: received packet "%s" on the in interface' % (self, pkt_S))
            #print('IF SEGMENT: ', pkt_S[1])
            if pkt_S[2] == '0':
                if pkt_S[1] == '0' or pkt_S[1] == '1': # not the last segment
                    self.packets0.append(pkt_S) # add packet to list of packets
                elif pkt_S[1] == '2': # is the last segment
                    self.packets0.append(pkt_S)
                    for i in self.packets0:
                        m0 = i[5:]
                        message0 = message0 + m0
                    print('received message 0: ', message0)

            elif pkt_S[2] == '1':
                if pkt_S[1] == '0' or pkt_S[1] == '1': # not the last segment
                    self.packets1.append(pkt_S) # add packet to list of packets
                elif pkt_S[1] == '2': # is the last segment
                    self.packets1.append(pkt_S)
                    for i in self.packets1:
                        m1 = i[5:]
                        message1 = message1 + m1
                    print('received message 1: ', message1)

            elif pkt_S[2] == '2':
                if pkt_S[1] == '0' or pkt_S[1] == '1': # not the last segment
                    self.packets2.append(pkt_S) # add packet to list of packets
                elif pkt_S[1] == '2': # is the last segment
                    self.packets2.append(pkt_S)
                    for i in self.packets2:
                        m2 = i[5:]
                        message2 = message2 + m2
                    print('received message 2: ', message2)


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

        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                #get packet from interface i
                #print("MTU: ", self.out_intf_L[i].mtu)
                pkt_S = self.in_intf_L[i].get()
                # if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                    data_S = pkt_S[5:]
                    dst_address = pkt_S[3:5]
                    if len(data_S) > self.out_intf_L[0].mtu:
                        # packet is too long
                        cur = 0
                        mes = data_S
                        messages = [] # variable to store parsed message
                        mes_num = int(pkt_S[2])
                        packets = [] #variable to store list of packets
                        while (len(mes)>self.out_intf_L[0].mtu - 5):
                            messages.append(''.join(mes[:self.out_intf_L[0].mtu - 5])) # add split messages to array
                            mes = mes[self.out_intf_L[0].mtu - 5:] # update message
                        if len(mes) > 0:
                                messages.append(mes)
                        for j in messages: # for each message
                            #print("CURRENT: ", cur)
                            #print("PACKET: ", pkt_S[1])
                            if cur == len(messages) - 1: # if current message is the last
                                #print("IN LAST")
                                if pkt_S[1] == '1':
                                    #print("IN IF LAST")
                                    packet = NetworkPacket(dst_address,j,1,2, mes_num) # create packet with updated if_last variable
                                    self.out_intf_L[0].put(packet.to_byte_S())
                                    print('%s: forwarding packet "%s"'\
                                      % (self, packet))
                                else:
                                    #print("IN IF NOT LAST")
                                    packet = NetworkPacket(dst_address,j,1,1, mes_num) # create packet with updated if_last variable
                                    self.out_intf_L[0].put(packet.to_byte_S())
                                    print('%s: forwarding packet "%s"' \
                                          % (self, packet))
                            else:
                                packet = NetworkPacket(dst_address,j,1,0, mes_num) # create packet that is not last
                                cur += 1 # update number of current packet
                                self.out_intf_L[0].put(packet.to_byte_S())
                                print('%s: forwarding packet "%s"' \
                                      % (self, packet))

                    # HERE you will need to implement a lookup into the
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i
                    self.out_intf_L[i].put(p.to_byte_S(), True)
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
