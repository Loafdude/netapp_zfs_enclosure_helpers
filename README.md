# netapp_zfs_enclosure_helpers
Python scripts to help manage netapp appliances


I use all-set_enclosure_leds.py in /etc/zfs/zed.d/

It works with my DS4486 which has 48 drives behind interposers

This makes calculating the path a little more difficult to set LED states

I'm sure this script could be easily modified to work with DS4246 and DS4243


--
mqtt_publish_enclosure.py 

This dumps all data available from sg_ses and publishes it to mqtt as a json object

this includes voltages, temperatures, fan speeds and failure states.


you will need to edit: 

-the device name (/dev/sg70 in my case)

-mqtt broker login information

I call this script from crontab on a regular basis and handle parsing of the data in node-red
