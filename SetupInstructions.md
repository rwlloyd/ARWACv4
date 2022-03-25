To add a service that is the last thing to start. Requires the Controller to be already paired
and automatically connect at startup (CONTROLLER ON AND SEARCHING BEFORE PI STARTUP).

sudo raspi-config
sudo apt-get update
sudo apt-get upgrade
sudo apt install python3-pip
pip3 install evdev
pip3 install pyserial
------------------------------
Arduino IDE

install ide
install https://playground.arduino.cc/Code/PIDLibrary/
install https://github.com/JChristensen/movingAvg

check sketches compile
-------------------------------
To pair the bluetooth controller:

launch in windows mode (X+Start)

sudo bluetoothctl
	scan on
	- get the mac address of the correct controller
	connect XX:XX:XX:XX:XX:XX
	pair XX:XX:XX:XX:XX:XX
	trust XX:XX:XX:XX:XX:XX
	exit

To add a service and make it run on startup

sudo nano /etc/systemd/system/remoteControl.service

----------------------------------------------------------
[Unit]
Description=Service for Bluetooth Remote Control
After=getty.target

[Service]
ExecStart=sh launcher.sh
WorkingDirectory=/home/pi/scripts
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target

---------------------------------------------------------

sudo chmod a+r /etc/systemd/system/remoteControl.service

sudo systemctl daemon-reload

sudo systemctl start remoteControl.service
- check everything is working
sudo systemctl stop remoteControl.service
sudo systemctl enable remoteControl.service

sudo reboot
- everything should work

- to help debug:
sudo systemctl status remoteControl.service
- to tail the cmd line output of the service...
journalctl -f -u remoteControl.service 

---------------------------------------------------------

GPS Unit Setup
Connect GPS with ethernet cable to router. 	
Get IP address of GPS unit. 	
May need to re-setup data stream within GPS: 		
	Use web browser go to GPS IP address. 		
	Click on NMEA / SBF out. 	
	If NMEA/SBF Output Streams is empty set up new NMEA stream. 
	New NMEA stream with port 28000. 
In python code change GPS IP address.

GPS parsing library 
pip3 install pynmea2

---------------------------------------------------------