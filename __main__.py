import ConfigParser
from network.network import RandomScaleFree
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
from time import sleep

if __name__ == "__main__":

	config = ConfigParser.ConfigParser()
	config.read('./config')

	link_type = config.get('main','Distribution')
	number_switches = int(config.get('main','MainSwitches'))
	number_hosts = 0
	number_servers = int(config.get('main','Datacenters'))
	ip = config.get('main','Ip')

	topology = RandomScaleFree(None, link_type, number_servers, number_switches, number_hosts)
	controller = RemoteController('c1', ip=ip, port=6633)

	print("Creating network")

	setLogLevel("info")
	network = Mininet(topo=topology, link=TCLink, controller=controller)

	print("Starting network")

	network.start()

	sleep(5)
	print("Running network")

	network.pingAll()

	cli = CLI(network)
	# CLI.do_xterm(cli)