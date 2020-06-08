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
NUM_HOLD_VIO_STR = "No. of Hold Violations"
TOTAL_NEG_SLACK_STR = 'Total Negative Slack:'
WNS_STR = 'Critical Path Slack:'
NUM_VIO_PTH_STR = 'No. of Violating Paths'

# Variable for different stages in the ASIC design flow.
#STAGES = ['synth', 'place', 'cts', 'post-cts', 'route', 'pt']
STAGES = ['place2', 'cts2', 'postcts2', 'route2']

# Labels used for columns of clock_qor report.
COLUMN_LABELS_CLOCK_QOR = ['Sinks', 'Levels', 'Clock Repeater Count',
                           'Clock Repeater Area', 'Clock Stdcell Area',
                           'Max Latency', 'Global Skew',
                           'Trans DRC Count', 'Cap DRC Count']

def format_qor_data(qor_report, stage):
    """
    Function to make the data easier to read 
    for CSV/text format.

    input: qor_report: list containing items to be organized.
    input: stage: string of current stage being processed.
    """
    func_worst = []
    func_best = []

    func_worst.append(["func_worst"])
    func_worst.append(["Clock Path", WNS_STR, TOTAL_NEG_SLACK_STR, NUM_VIO_PTH_STR])

    func_best.append(["func_best"])
    func_best.append(["Clock Path", HOLD_VIOLATION_STR, TOTAL_HOLD_VIOLATION_STR, NUM_HOLD_VIO_STR])
    i = 0
    for line in qor_report:
        rtn = line.find("Scenario")
        if rtn != -1:
            rtn = line.find('func_worst')
            if rtn != -1:
                func_worst.append([qor_report[i+1].split()[3], qor_report[i+2].split()[3], qor_report[i+3].split()[3], qor_report[i+4].split()[4]])
            rtn = line.find('func_best')
            if rtn != -1:
                func_best.append([qor_report[i+1].split()[3], qor_report[i+2].split()[3], qor_report[i+3].split()[3], qor_report[i+4].split()[4]])
        i += 1

    # Add stage variable to top of list.
    qor_report = []
    qor_report.append(["STAGE:", stage])
    for row in func_worst:
        qor_report.append(row)
    for row in func_best:
        qor_report.append(row)


    return qor_report

def get_qor_data(qor_report):
    """
        File to take a qor report file and grab important contents

        inputs: qor_report: .qor file that is a list of strings.

    """
    i = 0
    qor_report_temp = []
    for line in qor_report:
        rtn = line.find('Scenario')
        if rtn != -1:
            qor_report_temp.append(line)
            qor_report_temp.append(qor_report[i+1])
            rtn = line.find('func_worst')
            if rtn != -1:
                for k in range(2,12):
                    rtn = qor_report[i+k].find(WNS_STR)
                    if rtn != -1:
                        print(qor_report[i+k])
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(TOTAL_NEG_SLACK_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(NUM_VIO_PTH_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
            else:
                for k in range(2,12):
                    rtn = qor_report[i+k].find(HOLD_VIOLATION_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(TOTAL_HOLD_VIOLATION_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(NUM_HOLD_VIO_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
        i += 1

    qor_report = qor_report_temp

    return qor_report

def parse_clock_qor(qor_report, stage):
    """
        Function to parse clock_qor.
        input: qor_report: list containing report.
        input: stage: current stage 
    """
    i = 0
    clock_qor = []
    clock_qor.append(['Stage:', stage])
    for line in qor_report:
        rtn = line.find("Summary Reporting for Corner")
        if rtn != -1:
            k = 0
            clock_qor.append([line])
            clock_qor.append(['Clock Group', 'Attrs','Sinks','Levels','Clock Repeater Count',
                    'Clock Repeater Area', 'Clock Stdcell Area', 'Max Latency',
                    'Global Skew', 'Trans DRC Count', 'Cap DRC Count'])
            while qor_report[i + k].find('All Clocks') == -1:
                if qor_report[i + k].find('###') != -1:
                    clock_qor.append([qor_report[i+k]])
                if qor_report[i + k].find('CLK') != -1:
                    clock_qor.append([qor_report[i+k].split()])
                if qor_report[i + k].find('clk') != -1:
                    clock_qor.append([qor_report[i+k].split()])

                k += 1

        i += 1

    return clock_qor


def read_file_apr(file_path):
    """
        Function to read file and return the whole file.
        input: file_path - file path to qor files.
        output: qor_report - file contents returned.
    """
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

def write_qor_to_csv(top_design, reports, file_type, syn_or_apr):
    """
        Function to write results from all
        stages to a CSV file.

        input: top_design: string containing design name.
        input: reports: list containing data to be printed.
        input: file_type: type of report being parsed.
        input: syn_or_apr: string either containing "apr" or "syn" for 
            the /apr and /syn reports folders.
    """
    file_path = FOLDER_WRITE_PATH + top_design + '_' + file_type  \
        + '_' + syn_or_apr + '_reports_parsed.csv'
    with open(file_path, 'w') as csvfile:
        qor_writer = csv.writer(csvfile)
        for report in reports:
            for row in report:
                if type(row[0]) is list:
                    qor_writer.writerow(row[0])
                elif row is not None:
                    qor_writer.writerow(row)
    print("CSV file generated at path: " + file_path)


def write_data_to_text(top_design, reports, file_type, syn_or_apr):
    """
        Function that writes all the report 
        summaries to a text file.

        https://stackoverflow.com/questions/16796709/align-columns-in-a-text-file

        input: top_design: string indicating design name.
        input: reports: list of lists containing report data.
        input: file_type: type of report being parsed.
        input: syn_or_apr: string either containing "apr" or "syn" for 
            the /apr and /syn reports folders.
    """
    file_path = FOLDER_WRITE_PATH + top_design + '_' + file_type \
        + '_' + syn_or_apr + '_report_text.txt'
    with open(file_path, 'w') as txtfile:
        for stage in reports:
            for row in stage:
                if row is not None:
                    for val in row:
                        if type(val) is list:
                            for element in val:
                                txtfile.write(element.ljust(ALIGN_LENGTH))
                        elif val is not None:
                            txtfile.write(val.ljust(ALIGN_LENGTH))
                        else:
                            txtfile.write(" ".ljust(ALIGN_LENGTH))
                    txtfile.write('\n')
    print("text file generated at path: " + file_path)
