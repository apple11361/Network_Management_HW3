#!/usr/bin/env python
# -*- coding: utf8 -*-
# 2016.07.30 kshuang
 
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_5
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller import ofp_event
from ryu.ofproto import ofproto_v1_5_parser
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
 
class MyRyu(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_5.OFP_VERSION]
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
 
        for stat in ev.msg.body:
            if stat.port_no < ofproto.OFPP_MAX:
                self.normal_port.append(stat.port_no)
        
        if len(self.normal_port) == 2:
            print self.normal_port
            # h3 to s2
            match = parser.OFPMatch(in_port=self.normal_port[0])
            actions = [parser.OFPActionOutput(self.normal_port[1])]
            self.add_flow(datapath, 1, match, actions)
            # s2 to h3
            match = parser.OFPMatch(in_port=self.normal_port[1])
            actions = [parser.OFPActionOutput(self.normal_port[0])]
            self.add_flow(datapath, 1, match, actions)
        if len(self.normal_port) == 3:
            print self.normal_port
            
            # h1 to all
            match = parser.OFPMatch(in_port=self.normal_port[0])
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions)
            # h2 to all
            match = parser.OFPMatch(in_port=self.normal_port[1])
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions)
            # s2 to all
            match = parser.OFPMatch(in_port=self.normal_port[2])
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            self.add_flow(datapath, 1, match, actions)
        # clear port record after add flow entry
        self.normal_port = []
 
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #print datapath.id
        #table_id = 1
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)
        print mod
        
        #table_id = 2
        match = parser.OFPMatch(in_port=1)#, eth_dst='ff:ff:ff:ff:ff:ff'
        actions = [parser.OFPActionOutput(2)]
        #print match
        #print actions
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
 
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority+1, command=ofproto.OFPFC_ADD, match=match, instructions=inst)
        datapath.send_msg(mod)
        print mod
        
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