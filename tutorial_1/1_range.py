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
from datetime import datetime, timedelta
from time import sleep
import urllib2

# Set up the start and end dates.
start_date = "2005-01-24"
end_date = "2005-01-27"

# Specify the type of document we're interested in.
request_type = 'sadditional'

# Create a list of all the dates from the start to the end.
start = datetime.strptime(start_date, "%Y-%m-%d")
end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
date_range = [start + timedelta(n) for n in xrange((end - start).days)]

# Get the data for each date.
for current_date in date_range:
    requested_date = current_date.strftime("%Y-%m-%d")
    command = "http://api.fdsys.gov/link?collection=crec&link-type=html"
    command += "&type=" + request_type
    command += "&publishdate=" + requested_date

    print "Requesting data for", requested_date
    # Set up the connection to the server.
    # Give up after 30 seconds.
    response = urllib2.urlopen(command,
                               timeout=30)

    # Read the server's response.
    gpo_data = response.read()

    file_name = "crec_" + request_type + "_" + requested_date + ".htm"
    with open(file_name, 'w') as output_file:
        output_file.write(gpo_data)

    # Wait for 10 seconds.
    sleep(10)
