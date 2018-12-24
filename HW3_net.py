from mininet.log import setLogLevel,info
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.cli import CLI
 
 
def MininetTopo():
    net = Mininet()
    info("Create host nodes.\n")
    h1 = net.addHost("h1" , ip='192.168.1.11')
    h2 = net.addHost("h2" , ip='192.168.1.12')
    h3 = net.addHost("h3" , ip='192.168.2.13')
    #h4 = net.addHost("h4" , ip='192.168.3.13')
 
 
 
    info("Create switch node.\n")
    #s1 = net.addSwitch("s1",failMode = 'standalone')
    s1 = net.addSwitch("s1",failMode = 'secure',protocols = 'OpenFlow15')
    s2 = net.addSwitch("s2",failMode = 'secure',protocols = 'OpenFlow15')
 
    info("Create Links. \n")
    net.addLink(h1,s1)
    net.addLink(h2,s1)
    net.addLink(h3,s2)
    #net.addLink(h4,s1)
    #net.addLink(h4,s2)
    net.addLink(s1,s2)

    info("Create controller ot switch. \n")
    net.addController(controller=RemoteController,ip='10.0.2.15',port=6633)
 
    info("Build and start network.\n")
    net.build()
    net.start()
    info("Run the mininet CLI")
    CLI(net)
 
 
if __name__ == '__main__':
    setLogLevel('info')
    MininetTopo()
