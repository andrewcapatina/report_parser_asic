"""
    Andrew Capatina
    Description:
        This script parses a QOR report and creates a comma seperated
        list with values to be loaded into an excel spreadsheet.
"""

import pandas as pd
import os
import csv
import time

FOLDER_READ_PATH = "reports/"       # Location of reports to be parsed.
FOLDER_READ_PATH_SYN = "reports/syn/reports/" # Location of reports from synthesis.
FOLDER_READ_PATH_APR = "reports/apr/reports/" # Location of reports from place and route. 
FOLDER_WRITE_PATH = "outputs/"      # Location of the output parsed file.


# Update the below global variables if qor.rpt or clock_qor.rpt
# file reporting format changes.
ALIGN_LENGTH = 20   # The largest string to be displayed for reporting. 
HOLD_VIOLATION_STR = "Worst Hold Violation:"
TOTAL_HOLD_VIOLATION_STR = 'Total Hold Violation:'
TOTAL_NEG_SLACK_STR = 'Total Negative Slack:'
WNS_STR = 'Critical Path Slack:'

# Variable for different stages in the ASIC design flow.
STAGES = ['synth', 'place', 'cts', 'post-cts', 'route', 'pt']
#STAGES = ['place2', 'postcts2', 'route2']

# Labels used for columns of clock_qor report.
COLUMN_LABELS_CLOCK_QOR = ['Sinks', 'Levels', 'Clock Repeater Count',
                           'Clock Repeater Area', 'Clock Stdcell Area',
                           'Max Latency', 'Global Skew',
                           'Trans DRC Count', 'Cap DRC Count']


def format_clock_qor_data(clock_qor, timing_paths):
    """
        Function to remove any unneeded elements from
        the clock_qor data set.

        input: clock_qor: list containing clock_qor report.
        input: timing_paths: list containing all clock signals in design.

        output: list containing rows of information to be printed to CSV.
    """
    output = []
    flag = False
    for timing_path in timing_paths:
        for row in clock_qor:
            if row[0] == timing_path:
                # Trim uneeded elements.
                row = row[2:]
                output.append(row)
                flag = True
        if flag is False:
            row = row[2:]
            output.append(['-'])
        flag = False
    return output


def get_hold_times(qor_report):
    """
        Function to get worst hold time violations
        for each clock group.
        input: qor_report - text file containing contents
                            to search for. (list)
        output: hold_times - list of times taken from report.
    """
    hold_times = []
    for line in qor_report:
        rtn = line.find(TOTAL_HOLD_VIOLATION_STR)
        if rtn != -1:
            line = line.strip(TOTAL_HOLD_VIOLATION_STR)
            line = line.strip()
            hold_times.append(line)

    return hold_times


def get_timing_paths(qor_report):
    """
        Function to parse and get all timing paths in the QOR report.
        input: qor_report - text file containing contents
                            to search for. (list)
        output: timing_paths - list of timing paths of the current design.
    """
    timing_paths = []
    for line in qor_report:
        rtn = line.find('Timing Path Group')
        if rtn != -1:
            line = line.strip('Timing Path Group')
            line = line.strip("'")
            line = line.strip()
            line = line[:-1]
            timing_paths.append(line)

    return timing_paths


def get_tns(qor_report):
    """
        Function to get all total negative slack times in QOR.
        input: qor_report - list containing lines of file.
        output: tns_times - list containing times from file.
    """
    tns_times = []
    for line in qor_report:
        rtn = line.find(TOTAL_NEG_SLACK_STR)
        if rtn != -1:
            line = line.strip(TOTAL_NEG_SLACK_STR)
            line = line.strip()
            tns_times.append(line)

    return tns_times


def get_wns(qor_report):
    """
        Function to get all worst negative slack times from QOR.
        input: qor_report - list containing lines of file.
        output: wns_times - list of slack times.
    """
    wns_times = []
    for line in qor_report:
        rtn = line.find(WNS_STR)
        if rtn != -1:
            line = line.strip(WNS_STR)
            line = line.strip()
            wns_times.append(line)

    return wns_times


def get_worst_hold_violation(qor_report):
    """
        Function to get worst hold violation time from qor.
        input: qor_report - List containing lines of file.
        output: worst_hold_vio - Worst hold violation list.
    """
    worst_hold_vio = []
    for line in qor_report:
        rtn = line.find(HOLD_VIOLATION_STR)
        if rtn != -1:
            line = line.strip(HOLD_VIOLATION_STR)
            line = line.strip()
            worst_hold_vio.append(line)
    return worst_hold_vio


def parse_clock_qor(qor_report):
    """
        Function to parse clock_qor.
        input: qor_report: list containing report.
    """
    clocks = []
    for line in qor_report:
        rtn = line.find('CLK')
        if rtn != -1:
            clocks.append(line)

    clock_qor = []
    for clock in clocks:
        clock = clock.split()
        if(len(clock) > 3):  # Filter out unneeded elements of list.
            clock_qor.append(clock)

    return clock_qor


def read_file_apr(file_path):
    """
        Function to read file and return the whole file.
        input: file_path - file path to qor files.
        output: qor_report - file contents returned.
    """
    print(file_path)
    file_path = FOLDER_READ_PATH_APR + file_path
    try:
        with open(file_path) as fp:
            qor_report = fp.readlines()
    except:
        print("file path: " + file_path + " not found.")
        return 1

    return qor_report


def read_file_syn(file_path):
    """
        Function to read file and return the whole file.
        input: file_path - file path to qor files.
        output: qor_report - file contents returned.
    """
    print(file_path)
    file_path = FOLDER_READ_PATH_SYN + file_path
    try:
        with open(file_path) as fp:
            qor_report = fp.readlines()
    except:
        print("file path: " + file_path + " not found.")
        return 1

    return qor_report


def transpose_data(clock_qor):
    """
        Function to take input and transpose it.

    """
    clock_qor = pd.DataFrame(clock_qor)
    clock_qor = clock_qor.transpose()
    clock_qor = clock_qor.values.tolist()
    return clock_qor

def write_qor_to_csv(top_design, reports, syn_or_apr):
    """
        Function to write results from all
        stages to a CSV file.

        input: top_design: string containing design name.
        input: reports: list containing data to be printed.
        input: syn_or_apr: string either containing "apr" or "syn" for 
            the /apr and /syn reports folders.
    """
    file_path = FOLDER_WRITE_PATH + top_design + '_' + syn_or_apr \
       + '_reports_parsed.csv'
    with open(file_path, 'w') as csvfile:
        qor_writer = csv.writer(csvfile)
        for report in reports:
            for row in report:
                qor_writer.writerow(row)
    print("CSV file generated at path: " + file_path)


def write_data_to_text(top_design, reports, syn_or_apr):
    """
        Function that writes all the report 
        summaries to a text file.

        https://stackoverflow.com/questions/16796709/align-columns-in-a-text-file

        input: top_design: string indicating design name.
        input: reports: list of lists containing report data.
        input: syn_or_apr: string either containing "apr" or "syn" for 
            the /apr and /syn reports folders.
    """
    file_path = FOLDER_WRITE_PATH + top_design + '_' + syn_or_apr \
        + '_report_text.txt'
    with open(file_path, 'w') as txtfile:
        for report in reports:
            for row in report:
                for val in row:
                    if val is not None:
                        txtfile.write(val.ljust(ALIGN_LENGTH))
                    else:
                        txtfile.write(" ".ljust(ALIGN_LENGTH))
                txtfile.write('\n')
    print("text file generated at path: " + file_path)
