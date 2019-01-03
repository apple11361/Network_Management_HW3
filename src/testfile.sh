#!/bin/bash

#generate a packet from h1 to h2 (test general function)
ovs-appctl ofproto/trace s1 tcp,nw_src=192.168.1.11,nw_dst=192.168.1.12

#generate a packet from h1 to h2 port 22 (test filter)
#ovs-appctl ofproto/trace s1 tcp,nw_src=192.168.1.11,nw_dst=192.168.1.12,tcp_dst=22

#generate a packet from h1 to h3 (test group table)
#ovs-appctl ofproto/trace s1 tcp,nw_src=192.168.1.11,nw_dst=192.168.2.11
#ovs-appctl ofproto/trace s2 tcp,nw_src=192.168.1.11,nw_dst=192.168.2.11

#generate a packet from h3 to h2 (test group table)
#ovs-appctl ofproto/trace s2 tcp,nw_src=192.168.1.11,nw_dst=192.168.1.12
#ovs-appctl ofproto/trace s3 tcp,nw_src=192.168.1.11,nw_dst=192.168.1.12

exit 0
