from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.log import setLogLevel

REMOTE_CONTROLLER_IP = "192.168.0.10"

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        Host1 = self.addHost( 'h1', ip='192.168.1.11/24', mac='00:00:00:00:00:01' )
        Host2 = self.addHost( 'h2', ip='192.168.1.12/24', mac='00:00:00:00:00:02' )
        Host3 = self.addHost( 'h3', ip='192.168.2.11/24', mac='00:00:00:00:00:03' )
        Switch1 = self.addSwitch( 's1', protocols="OpenFlow13", mac='10:00:00:00:00:01' )
        Switch2 = self.addSwitch( 's2', protocols="OpenFlow13", mac='10:00:00:00:00:02' )
        Switch3 = self.addSwitch( 's3', protocols="OpenFlow13", mac='10:00:00:00:00:03' )

        # Add links
        self.addLink( Host1, Switch1 )
        self.addLink( Host2, Switch1 )
        self.addLink( Host3, Switch2 )
        self.addLink( Switch1, Switch2 )
        self.addLink( Switch1, Switch3 )
        self.addLink( Switch2, Switch3 )

#topos = { 'mytopo': ( lambda: MyTopo() ) }

if __name__ == '__main__':
    setLogLevel('info');
    topo = MyTopo()
    net = Mininet(topo=topo,
                  controller=None,
                  autoStaticArp=True)
    c0 = net.addController("c0",
                            controller=RemoteController,
                            ip=REMOTE_CONTROLLER_IP,
                            port=6633)
    net.start()
    CLI(net)
    net.stop()

