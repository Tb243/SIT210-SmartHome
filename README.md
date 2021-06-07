# SIT210-SmartHome
SmartHome hub MQTT

User Manual
Touchscreen is optional and it will work on a normal monitor with mouse – this was how I debugged the code before finally running on the small display. 
*Recommended you have a licensed electrician wire up the mains/power point for you. *

Hardware Required:
•	Raspberry Pi (3+)
•	Particle Argon
•	DHT22 Temperature and Humidity sensor
•	5v 10A Relay 
•	LED + 220Ω resistor (optional)
•	Touchscreen display - https://4dsystems.com.au/products/4dpi-35-ii

1.	Install and configure TFT by following the instructions for the display - https://4dsystems.com.au/mwdownloads/download/link/id/281/.
2.	Install Mosquitto MQTT broker with “sudo-apt-get install mosquito”.
3.	Install paho-mqtt with “pip3 install paho-mqtt”.
4.	Install PySimpleGUI by following https://packaging.python.org/tutorials/installing-packages/
5.	Download bootscript.py from github https://github.com/Tb243/SIT210-SmartHome
6.	If you want script to run on boot, you will need to chmod +x bootscript.py and add it to autolauncher – file location depends on version of Raspbian – in my case it was in /etc/xdg/lxsession/LXDE-pi/autolauncher which was different to a lot of the earlier tutorials available online.
7.	If you want to disable mouse cursor, install unclutter with “sudo apt-get install unclutter” and add “@unclutter -idle 0” to the same autostart file as above.
8.	Copy the argon file from github to Argon webIDE – may need to delete the include statements and import the libraries manually and flash.

Let me know if I missed anything, or if you want the full report with wiring diagram etc.
