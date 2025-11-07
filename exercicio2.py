from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink

class MyTopo(Topo):
    def build(self):
        # Hosts with standardized MACs
        h1 = self.addHost('h1', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', mac='00:00:00:00:00:04')
        h5 = self.addHost('h5', mac='00:00:00:00:00:05')

        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Conctions between switches
        self.addLink(s1, s2)
        self.addLink(s2, s3)

        # Conctions between switches and hosts
        self.addLink(s1, h1)
        self.addLink(s1, h2)
        self.addLink(s2, h3)
        self.addLink(s3, h4)
        self.addLink(s3, h5)

if __name__ == '__main__':
    topo = MyTopo()
    net = Mininet(topo=topo, controller=Controller, link=TCLink, autoSetMacs=True)
    net.start()

    
    print("--------------- Network information ---------------")
    print("Controlers:", net.controllers)
    print("Switches:", net.switches)
    print("Hosts:", net.hosts)

    print()
    for link in net.links:
        print(link)

    print("--------------- Ping test before flow rule changes ---------------")
    net.pingAll()
    h1, h4 = net.get('h1', 'h4')
    print(h1.cmd('ping -c 3', h4.IP()))

    print("--------------- Clearing flow rules ---------------")
    for sw in net.switches:
        sw.cmd('ovs-ofctl del-flows ' + sw.name)
    
    print("Flow rules cleared")

    print("--------------- Creating new flow rules ---------------")
    net.switches[0].cmd('ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:01,actions=output:2')
    net.switches[0].cmd('ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:01,actions=output:1')
    net.switches[1].cmd('ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:04,actions=output:2')
    net.switches[1].cmd('ovs-ofctl add-flow s2 dl_dst=00:00:00:00:00:04,actions=output:1')

    print('Flow rules created')
    
    print("--------------- Ping test after flow rule changes ---------------")
    print(h1.cmd('ping -c 3', h4.IP()))

    CLI(net)
    net.stop()