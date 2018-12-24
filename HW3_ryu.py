#!/usr/bin/env python
# -*- coding: utf8 -*-
# 2016.07.30 kshuang
 
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller import ofp_event
from ryu.ofproto import ofproto_v1_3_parser
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
 
 
    def send_port_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPPortStatsRequest(datapath, 0, ofp.OFPP_ANY)
        datapath.send_msg(req)
 
 
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        print datapath.id
        for stat in ev.msg.body:
            print stat.port_no
            print ofproto.OFPP_MAX
            if stat.port_no < ofproto.OFPP_MAX:
                self.normal_port.append(stat.port_no)
        
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
        #print datapath.id
        #table_id = 1
        next_table_id = 1
        inst = [parser.OFPInstructionGotoTable(next_table_id)]
        #inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
    
        mod = parser.OFPFlowMod(table_id = table_id, datapath=datapath, priority=priority, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)
        #print mod
        #---------------------------------------------------------------在這以下註解掉就是普通的可以互ping的情形
        #---------------------------------------------------------------我這裡加上第二個條件就是從port1來的 都接到port2去 所以從port1來的不會到port3
        #""" 
        table_id = 1
        #match = parser.OFPMatch(eth_dst='00:00:00:00:00:01')
        #actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        match = parser.OFPMatch()#, eth_dst='ff:ff:ff:ff:ff:ff'
        #actions = [parser.OFPActionOutput(2)]
        print actions
        #print match
        #print actions
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
        mod = parser.OFPFlowMod(table_id = table_id, datapath=datapath, priority=priority+1, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)

        match = parser.OFPMatch(eth_dst='00:00:00:00:00:03')
        actions = [parser.OFPActionOutput(1)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
        mod = parser.OFPFlowMod(table_id = table_id, datapath=datapath, priority=priority+2, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)

        #print mod
        #"""
    """
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
 
        
        cookie = cookie_mask = 0
        table_id = 10
        next_table_id = 11
        inst = [parser.OFPInstructionGotoTable(next_table_id)]
        mod = parser.OFPFlowMod(cookie = cookie ,cookie_mask = cookie_mask, table_id = table_id, datapath=datapath, priority=priority, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)

        cookie = cookie_mask = 0
        table_id = 11

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
        mod = parser.OFPFlowMod(cookie = cookie ,cookie_mask = cookie_mask, table_id = table_id, datapath=datapath, priority=priority, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)
        
        match = parser.OFPMatch(in_port=1)#, eth_dst='ff:ff:ff:ff:ff:ff'
        actions = [parser.OFPActionOutput(2)]
        print 
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority+1, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)
    """