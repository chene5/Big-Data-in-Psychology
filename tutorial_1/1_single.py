# -*- coding: utf-8 -*-
"""1_range.py
Example code for requesting data via the U.S. Government Printing Office
(GPO) API.

Created on Sun Feb 14 10:30:23 2016

Dates take the form:
Year-Month-Date
2005-02-14

@author: Eric Chen
"""
import datetime
import urllib2


# Specify the type of document we're interested in.
request_type = 'sadditional'

# Set the date to request.
requested_date = "2005-01-24"

# Construct the command.
command = "http://api.fdsys.gov/link?collection=crec&link-type=html"
command += "&type=" + request_type
command += "&publishdate=" + requested_date

print "Requesting data for", requested_date

# Set up the connection to the server.
response = urllib2.urlopen(command,
                           timeout=30)

# Read the server's response.
gpo_data = response.read()

file_name = "crec_" + request_type + "_" + requested_date + ".htm"
with open(file_name, 'w') as output_file:
    output_file.write(gpo_data)
print "Data saved in file", file_name
