from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink

class MyTopo(Topo):
    def build(self):
        # Hosts com MACs padronizados
        h1 = self.addHost('h1', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', mac='00:00:00:00:00:04')

        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Conexões entre switches
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s1, s4)

        # Conexões entre switches e hosts
        self.addLink(s2, h1)
        self.addLink(s2, h2)
        self.addLink(s3, h3)
        self.addLink(s4, h4)

if __name__ == '__main__':
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=RemoteController, link=TCLink, autoSetMacs=True)
    net.start()

    print("Informações de rede:")
    net.pingAll()
    print("Interfaces:")
    for host in net.hosts:
        print("\n{} ifconfig:".format(host.name))
        print(host.cmd('ifconfig'))

    print("Limpando regras de fluxo:")
    for sw in net.switches:
        sw.cmd('ovs-ofctl del-flows ' + sw.name)

    print("Adicionando regras baseadas em MAC:")
    net.switches[1].cmd('ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02,actions=output:2')
    net.switches[1].cmd('ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:01,actions=output:1')
    net.switches[2].cmd('ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:03,actions=output:1')
    net.switches[3].cmd('ovs-ofctl add-flow s4 dl_src=00:00:00:00:00:04,actions=output:1')

    print("Teste de conecrividade após regras:")
    h1, h2, h3, h4 = net.get('h1', 'h2', 'h3', 'h4')
    print(h1.cmd('ping -c 3 10.0.0.2'))
    print(h3.cmd('ping -c 3 10.0.0.4'))

    CLI(net)
    net.stop()