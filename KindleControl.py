#!/usr/bin/python
# easy_install pip
# sudo pip install evdev
# sudo pip install nmap
# sudo apt-get install python-paramiko
import paramiko, os.path, time
from select import select
from evdev import InputDevice, categorize, ecodes
from findip import find_ip_address_for_mac_address, scan_for_hosts

def main():
  kindle_mac = 'A0:02:DC:77:6B:57'
  kindle = KindleConnection(kindle_mac, 'root', 'root')
  
  # use 'evtest' to find out event and code.
  devices = map(InputDevice, ('/dev/input/event1', '/dev/input/event2'))
  devices = {dev.fd: dev for dev in devices}
  
  while True:
    r, w, x = select(devices, [], [])
    for fd in r:
      for event in devices[fd].read():
       if event.type == ecodes.EV_KEY and (event.code == 109 or event.code== 201) and event.value == 1L:
            print 'detected next'
	    kindle.NextPage()
       if event.type == ecodes.EV_KEY and event.code == 104 and event.value == 1L:
            print 'detected last'
	    kindle.LastPage()

class KindleConnection:

  def __init__(self, mac, username, password):
    self.mac = mac
    self.port = 22
    self.ip = None
    self.ip_range = '10.0.20.1-255'
    self.username = username
    self.password = password
    self._ssh = paramiko.SSHClient()
    self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

  def _Connection(self):
    if not self._IsConnected():
        xml = scan_for_hosts(self.ip_range)	
        self.ip = find_ip_address_for_mac_address(xml, self.mac)
        print self.ip
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(self.ip, self.port,
                          username = self.username, password = self.password)
    print "device connected"
    return self._ssh

  def _IsConnected(self):
    transport = self._ssh.get_transport() if self._ssh else None
    return transport and transport.is_active()

  def NextPage(self):
    self._Connection().exec_command('export DISPLAY=:0.0;xdotool mousemove 500 500 click 1')
    self._Connection().exec_command('lipc-set-prop com.lab126.powerd -i touchScreenSaverTimeout 1')

  def LastPage(self):
    self._Connection().exec_command('export DISPLAY=:0.0;xdotool mousemove 100 500 click 1')
    self._Connection().exec_command('lipc-set-prop com.lab126.powerd -i touchScreenSaverTimeout 1')

if __name__ == '__main__':
   main()    
