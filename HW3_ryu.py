#!/usr/bin/env python
# -*- coding: utf8 -*-
# 2016.07.30 kshuang

from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller import ofp_event
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
 
class MyRyu(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    normal_port = []
 
    def __init__(self, *args, **kwargs):
        super(MyRyu, self).__init__(*args, **kwargs)
 
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.send_port_stats_request(datapath)
 
    #Query the description of the switch
    def send_port_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPPortStatsRequest(datapath, 0, ofp.OFPP_ANY)
        datapath.send_msg(req)
 
    #Get the description of the switch
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        print '/**************************************/'
        print ('The description of switch %d:' % datapath.id)
        print ('The maximum number of physical ports: %d' % ofproto.OFPP_MAX)
        for stat in ev.msg.body:
            if stat.port_no < ofproto.OFPP_MAX:
                print ('The normal port: %d' % stat.port_no)
                self.normal_port.append(stat.port_no)
            else:
                print ('The port to communicate with controller: %d' % stat.port_no)

        if(datapath.id == 1):
            self.s1_init(datapath, ofproto, parser)
        elif(datapath.id == 2):
            self.s2_init(datapath, ofproto, parser)
        elif(datapath.id == 3):
            self.s3_init(datapath, ofproto, parser)

        if len(self.normal_port) == 2:
            print self.normal_port
            # h3 to s2
            match = parser.OFPMatch(in_port=self.normal_port[0])
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions,0)
            # s2 to h3
            match = parser.OFPMatch(in_port=self.normal_port[1])
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions,0)
            # s2 to h3
            match = parser.OFPMatch(in_port=3)
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions,0)

        if len(self.normal_port) == 3:
            print self.normal_port
            # h1 to all
            match = parser.OFPMatch(in_port=self.normal_port[0])
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions,0)
            # h2 to all
            match = parser.OFPMatch(in_port=self.normal_port[1])
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions,0)
            # s2 to all
            match = parser.OFPMatch(in_port=self.normal_port[2])
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions,0)
            # s2 to h3
            match = parser.OFPMatch(in_port=4)
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions,0)
        # clear port record after add flow entry
        self.normal_port = []
 
    def add_flow(self, datapath, priority, match, actions ,table_id):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        next_table_id = 1
        inst = [parser.OFPInstructionGotoTable(next_table_id)]
    
        mod = parser.OFPFlowMod(table_id = table_id, datapath=datapath, priority=priority, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)
        table_id = 1
        match = parser.OFPMatch()
        print actions
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
        mod = parser.OFPFlowMod(table_id = table_id, datapath=datapath, priority=priority+1, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)

        match = parser.OFPMatch(eth_dst='00:00:00:00:00:03')
        actions = [parser.OFPActionOutput(1)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
        mod = parser.OFPFlowMod(table_id = table_id, datapath=datapath, priority=priority+2, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)

    def s1_init(self, datapath, ofproto, parser):
        #****** Defnie table 0 to filter packets ******#
        # Drop packet if tcp_dst == 22
        match = parser.OFPMatch(eth_type=0x0800, ip_proto=6, tcp_dst=22)
        #match = parser.OFPMatch(in_port=22)
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS, [])]
        mod = parser.OFPFlowMod(table_id=0, datapath=datapath, priority=1,
                                command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)

        # Forward the rest of the packets to table 1
        match = parser.OFPMatch()
        inst = [parser.OFPInstructionGotoTable(1)]
        mod = parser.OFPFlowMod(table_id=0, datapath=datapath, priority=0,
                                command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)

        # Forward to table 2 if packets wanna go to h3
        match = parser.OFPMatch(eth_dst='00:00:00:00:00:03')
        port_1 = 2
        actions_1 = [parser.OFPActionOutput(port_1)]

        port_2 = 3
        actions_2 = [parser.OFPActionOutput(port_2)]

        weight_1 = 50
        weight_2 = 50
        watch_port = ofproto_v1_3.OFPP_ANY
        watch_group = ofproto_v1_3.OFPQ_ALL

        buckets = [
            parser.OFPBucket(weight_1, watch_port, watch_group, actions_1),
            parser.OFPBucket(weight_2, watch_port, watch_group, actions_2)]

        group_id = 1
        req = parser.OFPGroupMod(datapath, ofproto.OFPFC_ADD, ofproto.OFPGT_SELECT, group_id, buckets)

        datapath.send_msg(req)
            
        actions = [parser.OFPActionGroup(1)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, match=match, cookie=0, command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0, priority=10, instructions=inst)
        
        datapath.send_msg(mod)
    def s2_init(self, datapath, ofproto, parser):
        #****** Defnie table 0 to filter packets ******#
        # Drop packet if tcp_dst == 22
        match = parser.OFPMatch(tcp_dst=22)
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS, [])]
        mod = parser.OFPFlowMod(table_id=0, datapath=datapath, priority=1,
                                command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)

        # Forward the rest of the packets to table 1
        match = parser.OFPMatch()
        inst = [parser.OFPInstructionGotoTable(1)]
        mod = parser.OFPFlowMod(table_id=0, datapath=datapath, priority=0,
                                command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)
        
        # Forward to table 2 if packets wanna go to h1
        match = parser.OFPMatch(eth_dst='00:00:00:00:00:01')
        port_1 = 1
        actions_1 = [parser.OFPActionOutput(port_1)]

        port_2 = 3
        actions_2 = [parser.OFPActionOutput(port_2)]

        weight_1 = 50
        weight_2 = 50
        watch_port = ofproto_v1_3.OFPP_ANY
        watch_group = ofproto_v1_3.OFPQ_ALL

        buckets = [
            parser.OFPBucket(weight_1, watch_port, watch_group, actions_1),
            parser.OFPBucket(weight_2, watch_port, watch_group, actions_2)]

        group_id = 1
        req = parser.OFPGroupMod(datapath, ofproto.OFPFC_ADD, ofproto.OFPGT_SELECT, group_id, buckets)

        datapath.send_msg(req)
            
        actions = [parser.OFPActionGroup(1)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, match=match, cookie=0, command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0, priority=10, instructions=inst)
        
        datapath.send_msg(mod)

        # packets wanna go to h2
        match = parser.OFPMatch(eth_dst='00:00:00:00:00:02')
        port_1 = 1
        actions_1 = [parser.OFPActionOutput(port_1)]

        port_2 = 3
        actions_2 = [parser.OFPActionOutput(port_2)]

        weight_1 = 50
        weight_2 = 50
        watch_port = ofproto_v1_3.OFPP_ANY
        watch_group = ofproto_v1_3.OFPQ_ALL

        buckets = [
            parser.OFPBucket(weight_1, watch_port, watch_group, actions_1),
            parser.OFPBucket(weight_2, watch_port, watch_group, actions_2)]

        group_id = 2
        req = parser.OFPGroupMod(datapath, ofproto.OFPFC_ADD, ofproto.OFPGT_SELECT, group_id, buckets)

        datapath.send_msg(req)
            
        actions = [parser.OFPActionGroup(2)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, match=match, cookie=0, command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0, priority=10, instructions=inst)
        
        datapath.send_msg(mod)
    def s3_init(self, datapath, ofproto, parser):
        print 'Not implemented'
