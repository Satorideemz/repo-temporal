#!/usr/bin_/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import argparse

def myNetwork():
   #barra 29
   wan_net = []
   #barra 24
   lan_net = []
   routers = []
   hosts = []

   net = Mininet( topo=None,
                  build=False,
                  ipBase='10.0.0.0/8')

   info( '*** Adding controller\n' )
   info( '*** Add switches\n')
   for i in range(6):
     #cargo switches s1,s2,...
      nombre = 's' + str(i+1)
      lan_net.append(net.addSwitch(nombre + '_lan', cls=OVSKernelSwitch, failMode='standalone'))
      wan_net.append(net.addSwitch(nombre + '_wan', cls=OVSKernelSwitch, failMode='standalone'))

   info('*** Add routers\n')
   r_central = net.addHost('r_central', cls=Node, ip='')
   #indico que mi red usa ipv4
   r_central.cmd('sysctl -w net.ipv4.ip_forward=1')
   
   for i in range(6):
      #cargo routers r1,r2,...
      routers.append(net.addHost('r' + str(i+1), cls=Node, ip=''))
      routers[i].cmd('sysctl -w net.ipv4.ip_forward=1')

   info( '*** Add hosts\n')
   for i in range(6):
    #cargo hosts,h1,h2,...  
      ip = '10.0.' + str(i) + '.254/24'
      hosts.append(net.addHost('h' + str(i+1), ip=ip, defaultRoute=None))

   info( '*** Add links\n')
   for i in range(6):
     
      #son 6 sucursales mas broadcast y gateway
      #ips del nodo central
      #6,14,22,30,38,45
      r_central_ip = '192.168.100.' + str(6+8*i) + '/29'
      #ips de cada sucursal 1,9,17,25,33,41
      r_sucursal_ip_wan = '192.168.100.' + str(1+8*i) + '/29'
      #primer host de cada lan
      r_sucursal_ip_lan = '10.0.' + str(i) + '.1/24'
      #ultimo host de cada lan
      host_sucursal_ip = '10.0.' + str(i) + '.254/24'
      
      #links del central a mi wan
      net.addLink(r_central, wan_net[i], params1={'ip': r_central_ip})
      #links de mi wan a los routers
      net.addLink(routers[i], wan_net[i], params1={'ip': r_sucursal_ip_wan})
      #links de mi routers a la lan
      net.addLink(routers[i], lan_net[i], params1={'ip': r_sucursal_ip_lan})
      #links de mi lan a los hosts
      net.addLink(hosts[i], lan_net[i], params1={'ip': host_sucursal_ip})

   info( '*** Starting network\n')
   net.build()
   info( '*** Starting controllers\n')
   for controller in net.controllers:
       controller.start()

   info( '*** Starting switches\n')
   for switch in wan_net:
      switch.start([])
   
   for switch in lan_net:
      switch.start([])

   info( '*** Post configure switches and hosts\n')
   #armo tabla de routeo para el nodo central con mis subredes 
   for i in range(6):
      net['r_central'].cmd(f"ip route add 10.0.{i}.0/24 via 192.168.100.{1+8*i}")
   
   for i in range(6):
      #routeo la lan con el primer host
      routers[i].cmd(f'ip route add 10.0.{i}.0/24 via 10.0.{i}.1')
      routers[i].cmd(f'ip route add 0/0 via 192.168.100.{6+8*i}')
   
   for i in range(6):
      #routeo el la lan con el ultimo host
      hosts[i].cmd(f'ip route add 10.0.{i}.0/24 via 10.0.{i}.254')
      hosts[i].cmd(f'ip route add 0/0 via 10.0.{i}.1')

   CLI(net)
   net.stop()

if __name__ == '__main__':
   setLogLevel( 'info' )
   myNetwork()