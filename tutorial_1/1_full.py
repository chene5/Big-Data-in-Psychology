# -*- coding: utf-8 -*-
"""1_full.py
Example code for requesting data via the U.S. Government Printing Office
(GPO) API.

Portions of this code were adapted from code by the Sunlight Foundation
Congressional Words package.

Created on Sun Feb 14 10:30:23 2016

Dates take the form:
Year-Month-Date
2005-02-14

-s or --start   specifies the start date
-e or --end     specifies the end date.
                    This will retrieve up to BUT NOT INCLUDING this date.

@author: Eric Chen
"""
import sys
import os
import httplib
import urllib2
import socket
import datetime
import re
from time import sleep, strftime
import logging
import getopt


DEFAULT_START_DATE = "2005-01-01"
DEFAULT_END_DATE = "2016-01-01"
DEFAULT_REQUEST_TYPE = 'sadditional'

# Wait for this many seconds between API accesses
SLEEP_TIME_SECS = 10
# Number of accesses before giving up
ACCESS_ATTEMPTS_MAX = 3
# Timeout in seconds.
ACCESS_ATTEMPT_TIMEOUT = 30

GPO_HOME = './'
LOG_DIR = os.path.join(GPO_HOME, 'log')
RAW_DIR = os.path.join(GPO_HOME, 'raw')

# where should the scraper log the files it's downloaded?
RETRIEVER_LOG = os.path.join(LOG_DIR, 'retriever.log')


def url_backoff(attempt_count):
    sleep(1 * attempt_count)


def http_backoff(attempt_count):
    sleep(1 * 2**attempt_count)


def log_download_status(datestring, status, request_type=None):
    if request_type:
        # XXX: Not implemented.
        # log_name = 'scraper_' + request_type + '.log'
        pass
    if not os.path.exists(RETRIEVER_LOG):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        log_f = open(RETRIEVER_LOG, 'w')
        log_f.write('Date, Status\n')
        log_f.close()

    with open(RETRIEVER_LOG, 'a') as log_f:
        log_f.write('%s, %s\n' % (datestring, status))


def previously_retrieved(requested_date, request_type=None):
    if request_type:
        # XXX: Not implemented.
        # log_name = 'scraper_' + request_type + '.log'
        pass
    else:
        log_name = RETRIEVER_LOG
    datestring = requested_date.strftime("%y-%m-%d")
    if not os.path.exists(log_name):
        return False
    with open(log_name, 'r') as log_f:
        for line in log_f:
            if datestring in line and 'success' in line:
                print 'Previously retrieved: Record already exists.'
                return True
            if datestring in line and 'nosession' in line:
                print 'Previously retrieved: No data returned.'
                return True
    return False


def check_response(file_data):
    findtitle = re.compile(r'<title>(?P<title>.*)</title>')
    title = findtitle.search(file_data).group('title')
    if title == 'FDSys API Error':
        return False
    else:
        return True


def send_type_command(request_type, requested_date):
    """
    This function creates a request that is formatted for the GPO API.
    It retrieves a specific type of document for a specific date.
    The types are specified in the GPO API documentation:
    https://api.fdsys.gov/crec.html
    """
    command = "http://api.fdsys.gov/link?collection=crec&link-type=html"
    command += "&type={0}".format(request_type)
    command += "&publishdate={0}".format(requested_date)

    access_attempts = 1
    for attempt in range(0, ACCESS_ATTEMPTS_MAX):
        try:
            # Set up the connection to the server.
            response = urllib2.urlopen(command,
                                       timeout=ACCESS_ATTEMPT_TIMEOUT)
        except socket.timeout, e:
            print 'timeout: {0}'.format(e),
            log_download_status(requested_date, 'error: {0}'.format(e))
            logging.debug('timeout {} with date: {} at {} '.format(
                e, requested_date, strftime("%c")))
            access_attempts += 1
            url_backoff(access_attempts)
            continue
        except urllib2.URLError, e:
            print 'URLError: {0}'.format(e),
            log_download_status(requested_date, 'error: {0}'.format(e))
            logging.debug('URLError {} with date: {} at {} '.format(
                e, requested_date, strftime("%c")))
            access_attempts += 1
            url_backoff(access_attempts)
            continue
        except urllib2.HTTPError, e:
            print 'HTTPError: {0}'.format(e),
            log_download_status(requested_date, 'error: {0}'.format(e))
            logging.debug('HTTPError {} with date: {} at {} '.format(
                e, requested_date, strftime("%c")))
            access_attempts += 1
            http_backoff(access_attempts)
            continue
        except httplib.HTTPException, e:
            print 'HTTPException: {0}'.format(e)
            log_download_status(requested_date, 'error: {0}'.format(e))
            logging.debug('HTTPException {} with date: {} at {} '.format(
                e, requested_date, strftime("%c")))
            access_attempts += 1
            http_backoff(access_attempts)
            continue

    # If we tried and failed the max number of times, we failed.
    if access_attempts >= ACCESS_ATTEMPTS_MAX:
        print 'Retrieval failed!',
        log_download_status(requested_date, 'failed')
        logging.debug('Failure with date: {} at {} '.format(
            requested_date, strftime("%c")))
        return None

    # Check if the response was successful.
    # info = response.info()
    # print info

    # Read the server's response.
    file_data = response.read()

    if check_response(file_data):
        # print "FOUND!"
        return file_data
    else:
        # print "UNfound!"
        log_download_status(requested_date, 'nosession')
        return None


def save_htm(file_data, requested_date, info=None):
    """This function saves the data to a .htm file."""
    if not file_data:
        print "No data returned"
        return

    if info:
        file_name = "crec_" + info + "_" + requested_date + ".htm"
    else:
        file_name = "crec_" + requested_date + ".htm"

    with open(os.path.join(RAW_DIR, file_name), 'w') as output_file:
        output_file.write(file_data)
    print "Data saved in file", file_name

    # Record in the log that this date's data were successfully retrieved.
    log_download_status(requested_date, 'success')


def date_from_string(datestring):
    return datetime.datetime.strptime(datestring, "%Y-%m-%d")


def daterange_list(start, end):
    """Returns a list of date objects between a start and end date.
    start must come before end."""
    daterange = (end - start).days
    dates = [start + datetime.timedelta(n) for n in xrange(daterange)]
    return dates


def get_type_in_range(request_type, start_date, end_date):
    """Get documents of a particular type from the GPO API."""
    date_range = daterange_list(date_from_string(start_date),
                                date_from_string(end_date) + datetime.timedelta(days=1))

    # Create the save directory if necessary.
    if not os.path.exists(RAW_DIR):
        os.makedirs(RAW_DIR)

    # Get the data for each date.
    for requested_date in date_range:
        datestring = requested_date.strftime("%Y-%m-%d")
        print datestring, "...",
        if previously_retrieved(requested_date):
            # print "previously retrieved"
            continue

        # Check if the file has already been downloaded but not logged.
        file_name = "crec_" + request_type + "_" + datestring + ".htm"
        saveas = os.path.join('RAW_DIR', file_name)
        # print saveas,
        if os.path.exists(saveas):
            print "This file exists!"
            log_download_status(datestring, 'success')
            continue

        # Send the request command to the GPO API.
        data = send_type_command(request_type, datestring)

        # Save the data to an HTML file.
        save_htm(data, datestring, request_type)

        # Wait/sleep between API accesses.
        print "-- Sleep for: ",
        # Need to increment by 1 for the counter.
        sleep_time = SLEEP_TIME_SECS + 1
        for i in range(1, sleep_time):
            print "{0}...".format(sleep_time - i),
            sleep(1)
        print


def create_date(year, month, day):
    """
    This function combines the year, month, and day,
    divided by a "-" sign, into a single string object.
    For example: 2014-01-15
    This is the format that the GPO API (as well as Twitter,
    and others) use.
    """
    requested_date = "{0}-{1:02d}-{2:02d}".format(year, month, day)
    return requested_date


def create_dailydigest_command(requested_date):
    """This function creates a request that is formatted for the GPO API."""
    command = "http://api.fdsys.gov/link?collection=crec&section=dailydigest"
    command += "&publishdate=" + requested_date
    return command


def send_command(command):
    """This function sends the command to the API and downloads data."""
    # Set up the connection to the server.
    response = urllib2.urlopen(command)

    # Check if the response was successful.
    info = response.info()
    # Were expecting a pdf file, so abort if we get anything else.
    if info['Content-Type'] != 'application/pdf':
        return None

    # Read the server's response.
    file_data = response.read()

    return file_data


def save_file(file_data, requested_date):
    """This function saves the data to a file."""
    if not file_data:
        print "... No data returned"
        return

    file_name = "crec_dd_" + requested_date + ".pdf"
    with open(file_name, 'wb') as output_file:
        output_file.write(file_data)
    print "... Data saved in file", file_name


def usage():
    print __doc__


def parse_args(argv):
    """Parse any command line arguments."""

    # Set the default logging level to DEBUG
    # log_level = logging.INFO
    log_level = logging.DEBUG

    # This is the dictionary of arguments.
    arg_dict = {'start_date': DEFAULT_START_DATE,
                'end_date': DEFAULT_END_DATE,
                'type': DEFAULT_REQUEST_TYPE}

    try:
        opts, args = getopt.getopt(argv,
                                   "hds:e:t:",
                                   ["help",
                                    "debug",
                                    "start=",
                                    "end=",
                                    "type="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            log_level = logging.DEBUG
            print 'log level is at DEBUG'
        elif opt in ("-s", "--start"):
            arg_dict['start_date'] = arg
        elif opt in ("-e", "--end"):
            arg_dict['end_date'] = arg
        elif opt in ("-t", "--type"):
            arg_dict['type'] = arg

    # If this file is running as main, do logging.
    if __name__ == "__main__":
        logging.basicConfig(filename="log_gpo_tutorial.txt",
                            level=log_level,
                            filemode="a")
    logging.info('start: ' + strftime("%c"))

    return arg_dict


if __name__ == '__main__':
    # Parse any command line arguments.
    args_dict = parse_args(sys.argv[1:])
    start_date = args_dict['start_date']
    end_date = args_dict['end_date']
    request_type = args_dict['type']

    get_type_in_range(request_type, start_date, end_date)
