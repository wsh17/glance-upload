# glance-upload
Glance upload utility written in Python using TK for its GUI
this utility will upload images (guest OS) to an openstack cloud using the python CLI libraries
# Authenication
this utility leverages the openstack rc files for flexability of talking to different cloud so first
run you "tenant name-openrc.sh" to authencate
$ source "tenant name-openrc.sh"
Enter you user name's password
# Run the upload utility
next you will need to run the utility under python
$ python glance-uploadV9R3.py
Next you will see a simple gui. 
the utility only supports non-container formats, so Raw, QCOW2, VHD, ...VMDK, ISO.


