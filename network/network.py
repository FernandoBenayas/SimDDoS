import networkx as nx
import random
from mininet.topo import Topo

# -*- coding: utf-8 -*-
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
#
# Copyright (c) 2018  Fernando Benayas  <ferbenayas94@gmail.com>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v2.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.html.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
#title           : scalefree.py
#date created    : 20/02/2018
#python_version  : 3.5.1
#notes           :
__author__ = "Fernando Benayas"
__license__ = "GPLv2"
__version__ = "0.1.0"
__maintainer__ = "Fernando Benayas"
__email__ = "ferbenayas94@gmail.com"

"""This program can change the license header inside files.
"""
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

class RandomScaleFree(Topo):
	"""
		RandomScaleFree is inherited from Topo and defines the network to be created.

			Args:
					- seed (int): seed from wich the network topology will be created.
					- link_type (str): specifies the type of links to be used.
					- datac (int): specifies the number of datacenters to be created
					- n (int): number of nodes to be created
					- h (int): number of hosts to be created
					- namespace (duple): number of elements in the network, in order to name each element
					correctly and avoid using names already used

			Return:
					RandomScaleFree object.

			Attributes:
					- G (Graph): Networkx graph.

			Methods:
					- topify: Given a Graph represeting the topology to be created, it creats a Topo mininet object.
					- add_datacenters: Adds hosts and links to the topology representing datacenters
					- random_access: creates the access links with various bandwidths

		"""
	def __init__(self, seed, link_type = "equal", servers=0, n=100, h=0, namespace = None):
		Topo.__init__(self)
		G=nx.Graph()

		if not seed:
			seed = random.randint(1, 10000)

		G=nx.scale_free_graph(n=n, seed=int(seed))
		G.remove_edges_from(G.selfloop_edges())

		self.topify(G, h, link_type, namespace)
		if servers > 0:
			self.add_server(h, servers)

		self.trim()

		print("----------- Check cardinality of elements in simulation -----------")
		print(self.switches())
		print(self.hosts())
		print(self.links())

	def topify(self, randomscale=None, ho=0, link_type="equal", namespace=None):
		"""
		Translates the topology of the networkx graph into a mininet topology,
		turning nodes into switches and edges into links

			Args:
				- randomscale (networkx graph): graph to be topified
				- ho (int): number of hosts to be added
				- link_type (str): type of links to be added
				- namespace (duple): number of elements in the network, in order to name each element
					correctly and avoid using names already used

			Returns:
				None.

		"""
		nodes = list(randomscale.nodes())
		edges = randomscale.edges()
		bw = 1000
		lat = '3ms'

		switches = []
		hosts = []
		links = []

		for s in range(len(nodes)):
			if namespace is not None:
				switches.append(self.addSwitch('s{}'.format(s+1+namespace[0])))
			else:
				switches.append(self.addSwitch('s{}'.format(s+1)))

		for e in range(len(edges)):
			if edges[e] in links or edges[e][::-1] in links:
				continue
			else:
				links.append(edges[e])
				if namespace is not None:
					self.addLink('s{}'.format(edges[e][0] + 1 + namespace[0]),
								's{}'.format(edges[e][1] + 1 + namespace[0]), bw=bw, delay=lat)
				else:
					self.addLink('s{}'.format(edges[e][0]+1), 's{}'.format(edges[e][1]+1),
					bw=bw, delay=lat)

		for h in range(ho):
			if namespace is not None:
				hosts.append(self.addHost("h{}".format(h+1+namespace[1])))
			else:
				hosts.append(self.addHost("h{}".format(h+1)))
			links.append(self.addLink(random.choice(switches), hosts[len(hosts)-1], bw=self.random_access(link_type),delay=lat))

	def add_server(self, n_ho, servers):
		"""
		Adds host and link to the topology representing a server

			Args:
				- n_sw (int): number of switches currently in the network
				- n_ho (int): number of hosts to currently in the network
				- servers (int): number of servers to be created

			Returns:
				None.
		"""

		for n in range(servers):
			sw_connect = random.sample(self.switches(), k=1)
			self.addHost("h{}".format(n_ho+n+1))
			self.addLink("h{}".format(n_ho+n+1), sw_connect[0], bw = 1000, lat = '3ms')


	def trim(self):
		"""
		Creates links in switches with only one link
		in the main network

			Args:
				None.

			Returns:
				None.

		"""
		# We get a list of switches, links, and we define two auxiliary variables
		switches = self.switches()
		links = self.links()
		counter = 0
		other_switch = ''

		# We go through the list of switches, and when we detect
		# a switch that doesn't have links or only has them with itself,
		# we add a link with other switch
		for s in switches:
			for l in links:
				if s == l[0]:
					if l[1] == other_switch:
						continue
					else:
						counter += 1
						other_switch = l[1]
				if s == l[1]:
					if l[0] == other_switch:
						continue
					else:
						counter += 1
						other_switch = l[0]

			if counter == 1:
				switches_b = self.switches()
				switches_b.remove(other_switch)
				switches_b.remove(s)

				self.addLink(s, random.choice(switches_b), bw = 1000, lat = "3ms")
			counter = 0
			other_switch = ''


	# Randomize selection of access bandwidth in hosts
	def random_access(self, link_type):
		"""
		Randomize selection of access bandwidth in hosts.

			Args:
				- link_type (str): type of link regarding badnwidth.

			Returns:
				bandwidth (int): int indicating bandwidth of the link to be added.
		"""
		bw_table = [3, 10, 20, 50, 300]

		if link_type == "badwifi":
			return bw_table[0]
		elif link_type == "wifi":
			return bw_table[1]
		elif link_type == "xdsl":
			return bw_table[2]
		elif link_type == "fiber50":
			return bw_table[3]
		elif link_type == "fiber300":
			return bw_table[4]
		else:
			return bw_table[random.randint(0, 4)]