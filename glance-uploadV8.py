#!/usr/bin/env python
########################################################################################## 
#
# Author: Bill Harper
# Example Python Script for OpenStack to Upload an OS image to Glance using the Python
# client side Methods which are part of the client command line.
#  
# These Classes and Methods are not well documented, this is an example to show how to use
# them in practice.
# 
##########################################################################################
from Tkinter import *
import tkFileDialog
import os
#
# OpenStack Imports for Keystone, Nova and Glance into new namespace of ksclient, nvclient
# and glclient so that no one method conflicts with another :-) Yes we love you OpenStack
# 
import keystoneclient.v2_0.client as ksclient
import novaclient.v1_1.client as nvclient
import glanceclient.v1.client as glclient
#
##########################################################################################


##########################################################################################
#
# Class file uploadApp - setup the frame, self space and call the GUI function
#
##########################################################################################

class uploadApp(Frame):	

  def __init__(self, master):
    Frame.__init__(self, master)
    self.master = master
    
    self.GUI()

##########################################################################################   
#
# Setup the basic GUI, read image name, choose image type, and then choose file and upload
#
##########################################################################################

 		
  def GUI(self):
  
    imageName   = StringVar() 
    guestFormat = StringVar()
    imageFile   = StringVar()
    var1        = StringVar()
    value       = StringVar()     
    imageName = ""

    hostname = "api-trial2.client.metacloud.net" # api endpoint
    tenantname = "trial-admin"
    username = "trial-admin"
    password = "" 

    response = os.system("ping -q -c 1 " + hostname)

    # Check to see if we have network connectivity before we make a call to the openstack API's
    # Check if network is true or false. 
    # and then check the response...
    #
    
    if response == 0:
      #print hostname, 'is up!'
      hstatus="is up!"
    else:
      print hostname, 'is down, exiting with error conndition, host not available'
      hstatus="is down!"
      sys.exit()
    # 
    # Forcing login to both Keystone and Nova end points, I need both
    nvtoken = nvclient.Client(auth_url='http://api-trial2.client.metacloud.net:5000/v2.0', username='trial-admin', api_key='*******', project_id='Trial2-Admin')
    kstoken = ksclient.Client(username='trial-admin', password='*********',tenant_name='Trial2-Admin', auth_url='http://api-trial2.client.metacloud.net:5000/v2.0')
    
    # setup a trace on self.namevar to make sure we can validate a name is entered

    self.namevar = StringVar()
    self.namevar.trace('w', self.validate)

    self.text = Label(root, text="Enter the OS Name for OpenStack:").grid(row=0)
    Label(root, text="Upload Status: IDLE ").grid(row=11)

    # Need to check if we have a real image valid name, using validate to gray out before name is entered i.e. self.namevar is always validated

    imageName = Entry(root, textvariable=self.namevar, bd = 3, width=40)
    imageName.grid(row=0, column=1)

    # User buttons for image type Choice of raw, qcow2 and vmdk
    # Force a Default of RAW to start with

    var1.set("raw")
    self.submit = Radiobutton(root, text="raw", variable=var1, value="raw")
    self.submit.grid(row=2, column=1, sticky=W)
    self.submit = Radiobutton(root, text="qcow2", variable=var1, value="qcow2")
    self.submit.grid(row=3, column=1, sticky=W)
    self.submit = Radiobutton(root, text="vmdk", variable=var1, value="vmdk")
    self.submit.grid(row=4, column=1, sticky=W)

    # Button to choose file and push upload.

    self.file = Button(root, text='Choose the file and Upload', state=DISABLED, command=lambda: self.uploadImage(nvtoken,kstoken,guestFormat,imageName,var1))
    self.file.grid(row=5, column=1, sticky=W, pady=4)

    # Exit button, just exit

    self.exit = Button(root, text='Exit', command=root.quit)
    self.exit.grid(row=6, column=1, sticky=W, pady=4)
    Label(root, text="Upload Status: IDLE ").grid(row=11)
    Label(root, text="End Point Status:  %s " % hstatus ).grid(row=10)
    # Debug it
    DBUG=False
    if DBUG:
      print ("namevar is = %s" % self.namevar.get())
      print ("exit Guest format= %s" % guestFormat.get())
      print ("exit var1 format= %s" % var1.get())

  ##########################################################################################
  #
  # Validate function for name entered, tricky python thing, makes sure there is a string, 
  # otherwise gray out choose file option, force raw on OS guest type as default
  #
  ##########################################################################################
  #
  def validate(self, imageName, index, mode):
     self.file.config(state=(NORMAL if self.namevar.get() else DISABLED))
     return True
  ##########################################################################################
  # 
  # Upload function, it asks for the file name choice via a menu, the does its upload to 
  # glance based on name, guest OS type, and file name, container is assumed bare. 
  #
  ########################################################################################## 
  def uploadImage(self,nvtoken,kstoken,guestFormat,imageName,var1):   
    realimagename=imageName.get()
    realguestFormat=guestFormat.get()
    realvar1=var1.get()
    #uploadStatus = StringVar()
    filenamestate=False
    DBUG=False
    if DBUG:
      print ("imageName = %s" % imageName)
      print ("realimage is %s" % realimagename)
    
      print ("guestFormat = %s" % guestFormat)
      print ("realguestformat is %s" % realguestFormat)
      print ("var1 = %s" % var1)
      print ("realvar1 is %s" % realvar1)
    
    Label(root, text="Upload Status: IDLE ").grid(row=11)
    self.update_idletasks()
    while filenamestate == False:
      #Get the file name to open
      image_file = tkFileDialog.askopenfilename(filetypes = (("OS Image Type", "*.img"), ("OS Image Type", "*.qcow2"), ("All files", "*.*")))
      # Don't allow a blank file name, if so return
      if os.path.isfile(image_file):
          filenamestate=True
      else: 
          filenamestate=False
          return #user hit cancel
    glance_endpoint = kstoken.service_catalog.url_for(service_type='image',endpoint_type='publicURL')
    glance = glclient.Client(glance_endpoint, token=kstoken.auth_token)
    DBUG = False
    if DBUG:
      print("image file name %s" % image_file)
      print("image filename length %s" % len(image_file))
    self.update_idletasks() # force the GUI to update 
    with open(image_file) as fimage:
      Label(root, fg = "red", text="Upload Status: Image %s is UPLOADING ... " % realimagename).grid(row=11)
      self.update_idletasks()
      glance.images.create(name=realimagename, is_public=False, disk_format=realvar1, container_format="bare", data=fimage)
      Label(root, fg="dark green", text="Upload Status: Image %s has been uploaded and CREATED." % realimagename).grid(row=11)
      return
##########################################################################################
#
# main() call tk, set the window size call the gui, loop
#
##########################################################################################
  
root = Tk()
root.geometry("620x220+300+400")
root.title("BOUU-V8 - Bills OpenStack Upload Utility V1.8")
app = uploadApp(root)
root.mainloop()
