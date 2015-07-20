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

import ttk
from Tkinter import *
import tkFileDialog
import os
from urlparse import urlparse

###########################################################################################
# OpenStack Imports for Keystone, Nova and Glance into new namespace of ksclient, nvclient
# and glclient so that no one method conflicts with another :-) Yes we love you OpenStack
###########################################################################################

import keystoneclient.v2_0.client as ksclient
import novaclient.v1_1.client as nvclient
import glanceclient.v1.client as glclient

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


    #################################################################################
    # Check if env Varables above were set, if not kick out and tell user to run .sh 
    # script from OpenStack.  
    #################################################################################

    try:  
      os.environ["OS_AUTH_URL"]
      os.environ["OS_USERNAME"]
      os.environ["OS_PASSWORD"]
      os.environ["OS_TENANT_NAME"]
    except KeyError: 
      print " "
      print "\a"
      print "Glance-Upload-Tool Error: Please set the environment variable OS_AUTH_URL, OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME properly"
      # key doesn't exist in dict
      print "Please run you OpenStack Login Script as it will set all of these automatically for you, we use these to login to the cloud"
      print " "
      sys.exit(1)
    
    #################################################################################
    # We're going to use the login script varables for authenication to OpenStack   #
    # We need to check if there set and error out and exit gracefully (above)       #
    # Next we put the information into python variables so we can use it            #
    #################################################################################

    os_auth_url    = os.environ[('OS_AUTH_URL')] 
    os_username    = os.environ[('OS_USERNAME')]
    os_password    = os.environ[('OS_PASSWORD')]
    os_tenant_name = os.environ[('OS_TENANT_NAME')]
     
    ################################################################################
    # Check to see if we have network connectivity before we make a call to the 
    # openstack API's Check if network is true or false. 
    # and then check the response... We will use urlparse function to get the host
    # name to ping. What a cool function urlparse.
    ################################################################################
    
    parsed = urlparse(os_auth_url)
    #print parsed.hostname
    hostname=parsed.hostname
    response = os.system("ping -q -c 1 " + hostname)
    if response == 0:
      #print hostname, 'is up!'
      hstatus="is up!"
    else:
      print " "
      print "\a"
      print hostname, 'is down or not reachable, exiting with error conndition'
      hstatus="is down!"
      sys.exit()

    ############################################################################## 
    # using env vars to login to both Keystone and Nova end points using the OS 
    # environment varables that the OpenStack script setup - call the API's 
    # First we need to make sure the tenant, user, password, auth_url are correct
    ##############################################################################
    
    try:
      kstoken = ksclient.Client(username=os_username, password=os_password,tenant_name=os_tenant_name, auth_url=os_auth_url)
      nvtoken = nvclient.Client(auth_url=os_auth_url, username=os_username, api_key=os_password, project_id=os_tenant_name)
    except:
      sys.exc_clear()
      print " "
      print "\a"
      print "Error with your OpenStack credientals, your user, auth_url, tenant or password are incorrect. Probably your password." 
      print "Please re-run you OpenStack Login Script as it will set all of these automatically for you again."  
      print " "
      sys.exit(1)
           
    ##################################################################################
    # Note kstoken.auth_token is the token from keystone needed ... for any real work
    ##################################################################################
    
    # print kstoken.auth_token
    
    ##################################################################################
    # setup a trace on self.namevar to make sure we can validate a name is entered
    # this is a tricky python technique to gray out fields until data is entered
    ##################################################################################

    self.namevar = StringVar()
    self.namevar.trace('w', self.validate)

    self.text = Label(root, text="Please Enter the OS Name for OpenStack:").grid(row=0)
    Label(root, text="Upload Status: IDLE ").grid(row=11)
    
    ##################################################################################
    # Need to check if we have a real valid image name, using validate to gray out 
    # before name is entered i.e. self.namevar is always validated
    ##################################################################################
    
    imageName = Entry(root, textvariable=self.namevar, bd = 3, width=40)
    imageName.grid(row=0, column=1)
    
    ##################################################################################
    # User buttons for image type Choice of raw, qcow2 and vmdk
    # Force a Default of RAW to start with on the user interface
    ##################################################################################
    
    var1.set("raw")
    # Allow user to change format type
    self.submit = Radiobutton(root, text="RAW - KVM Raw performance disk image format", variable=var1, value="raw")
    self.submit.grid(row=2, column=1, sticky=W)
    self.submit = Radiobutton(root, text="QCOW2 - KVM Copy on Write V2 image format", variable=var1, value="qcow2")
    self.submit.grid(row=3, column=1, sticky=W)
    self.submit = Radiobutton(root, text="VMDK - VMWare VMDK > V7 Raw Image ", variable=var1, value="vmdk")
    self.submit.grid(row=4, column=1, sticky=W)
    self.submit = Radiobutton(root, text="VHD - Hyper-V Image", variable=var1, value="vhd")
    self.submit.grid(row=5, column=1, sticky=W)
    self.submit = Radiobutton(root, text="VDI - Virtual Box Image", variable=var1, value="vdi")
    self.submit.grid(row=6, column=1, sticky=W) 
    self.submit = Radiobutton(root, text="ISO Disk Image (not recommended)", variable=var1, value="iso")
    self.submit.grid(row=7, column=1, sticky=W)

    # Button to choose file and upload all at one time.  The quickest way, I could change it but 2 steps here. 

    self.file = Button(root, text='Choose the file and Upload', state=DISABLED, command=lambda: self.uploadImage(nvtoken,kstoken,guestFormat,imageName,var1))
    self.file.grid(row=8, column=1, sticky=W, pady=4)

    # Exit button, just exit

    self.exit = Button(root, text='Exit', command=root.quit)
    self.exit.grid(row=9, column=1, sticky=W, pady=4)
    Label(root, text="Upload Status: Idle                                  ").grid(row=11)
    Label(root, text="End Point Status:  %s               " % hstatus ).grid(row=10)
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
  
  def validate(self, imageName, index, mode):
     self.file.config(state=(NORMAL if self.namevar.get() else DISABLED))
     return True
     
  ##########################################################################################
  # 
  # Upload function, it asks for the file name choice via a menu, then it does its upload to 
  # glance based on name, guest OS type, and file name, container is assumed bare only at this 
  # time.  No support for ami, aki or akr yet.  
  #
  ########################################################################################## 
  
  def uploadImage(self,nvtoken,kstoken,guestFormat,imageName,var1):
  
    #################################################
    # Now get the contents of the varable using get()   
    ##################################################
  
    realimagename=imageName.get()
    realguestFormat=guestFormat.get()
    realvar1=var1.get()
    filenamestate=False
    DBUG=False
    if DBUG:
      print ("imageName = %s" % imageName)
      print ("realimage is %s" % realimagename)
    
      print ("guestFormat = %s" % guestFormat)
      print ("realguestformat is %s" % realguestFormat)
      print ("var1 = %s" % var1)
      print ("realvar1 is %s" % realvar1)
    
    Label(root, text="Upload Status: IDLE                        ").grid(row=11)
    self.update_idletasks()
    while filenamestate == False:
      #Get the file name to open
      image_file = tkFileDialog.askopenfilename(filetypes = (("OS Image Type", "*.img"), ("OS Image Type", "*.qcow2"), ("All files", "*.*")))
      # Don't allow a blank local file name, if so just return
      if os.path.isfile(image_file):
          filenamestate=True
      else: 
          filenamestate=False
          return #user hit cancel so return
          
    ##################################################################
    # Ask the Service Catalog for the glance public url end point
    ##################################################################
    
    glance_endpoint = kstoken.service_catalog.url_for(service_type='image',endpoint_type='publicURL')
    
    ######################################################################
    # using the end point, feed in the token stored in kstoken.auth_token
    ######################################################################
    
    glance = glclient.Client(glance_endpoint, token=kstoken.auth_token)
    DBUG = False
    if DBUG:
      print("image file name %s" % image_file)
      print("image filename length %s" % len(image_file))
    #self.update_idletasks() # force the GUI to update text as I change it 
    
    #########################################################################
    # Finially we can go ahead and upload the image to glance.images.create
    #########################################################################
    
    with open(image_file) as fimage:
      Label(root, fg = "red", text="Upload Status: %s is now UPLOADING " % realimagename).grid(row=11)
      self.update_idletasks()
      glance.images.create(name=realimagename, is_public=False, disk_format=realvar1, container_format="bare", data=fimage)
      Label(root, fg="dark green", text="Upload Status: Image %s was CREATED" % realimagename).grid(row=11)
      return
      
##########################################################################################
#
# main() call tk, set the window size call the gui, loop
#
##########################################################################################
  
root = Tk()
root.geometry("700x500+500+500")
root.title("BOUUV9R3 - Bill's OpenStack Upload Utility")
app = uploadApp(root)
root.mainloop()
