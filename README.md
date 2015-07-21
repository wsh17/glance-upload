# glance-uploadV9R3 for OpenStack
Glance upload utility written in Python using TK for its GUI
this utility will upload images (guest OS) to an openstack cloud using the python CLI libraries
# Author
Bill Harper from Metacloud
# Inspiration for this utility
This utility was inspired by the need to learn the openstack API/Python bindings as well as 
have a more reliable and faster way to import images into OpenStack.  This code basically maps
the small guest OS into memory as as an object, then calls openstack image create to imgest it
# Authenication
this utility leverages the openstack rc files for flexability of talking to different cloud so first
run you "tenant name-openrc.sh" to authencate
$ source "tenant name-openrc.sh"
Enter you user name's password
# Run the upload utility
next you will need to run the utility under python
$ python glance-uploadV9R3.py
Next you will see a simple gui to name you guest os in openstack, pick a format, the choose a file to upload
the utility only supports non-container formats, so Raw, QCOW2, VHD, ...VMDK, ISO.
# 

