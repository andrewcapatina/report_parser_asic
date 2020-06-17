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
FOLDER_READ_PATH_SYN = "../syn/reports/" # Location of reports from synthesis.
FOLDER_READ_PATH_APR = "../apr/reports/" # Location of reports from place and route. 
FOLDER_WRITE_PATH = "outputs/"      # Location of the output parsed file.


# Update the below global variables if qor.rpt or clock_qor.rpt
# file reporting format changes.
ALIGN_LENGTH = 25   # The largest string to be displayed for reporting. 
HOLD_VIOLATION_STR = "Worst Hold Violation:"
TOTAL_HOLD_VIOLATION_STR = 'Total Hold Violation:'
NUM_HOLD_VIO_STR = "No. of Hold Violations"
TOTAL_NEG_SLACK_STR = 'Total Negative Slack:'
WNS_STR = 'Critical Path Slack:'
NUM_VIO_PTH_STR = 'No. of Violating Paths'

# Variable for different stages in the ASIC design flow.
STAGES = ['place2', 'cts2', 'postcts2', 'route2']

# Labels used for columns of clock_qor report.
COLUMN_LABELS_CLOCK_QOR = ['Sinks', 'Levels', 'Clock Repeater Count',
                           'Clock Repeater Area', 'Clock Stdcell Area',
                           'Max Latency', 'Global Skew',
                           'Trans DRC Count', 'Cap DRC Count']

def format_qor_data_apr(qor_report, stage):
    """
    Function to make the data easier to read 
    for CSV/text format.

    input: qor_report: list containing items to be organized.
    input: stage: string of current stage being processed.
    """
    func_slow = []
    func_worst = []
    func_best = []

    func_slow.append(["func_slow"])
    func_slow.append(["Clock Path", WNS_STR, TOTAL_NEG_SLACK_STR, NUM_VIO_PTH_STR, HOLD_VIOLATION_STR, TOTAL_HOLD_VIOLATION_STR, NUM_HOLD_VIO_STR])

    func_worst.append(["func_worst"])
    func_worst.append(["Clock Path", WNS_STR, TOTAL_NEG_SLACK_STR, NUM_VIO_PTH_STR])

    func_best.append(["func_best"])
    func_best.append(["Clock Path", HOLD_VIOLATION_STR, TOTAL_HOLD_VIOLATION_STR, NUM_HOLD_VIO_STR])

    test_worst = []
    test_best = []

    test_worst.append(["test_worst"])
    test_worst.append(["Clock Path", WNS_STR, TOTAL_NEG_SLACK_STR, NUM_VIO_PTH_STR])

    test_best.append(["test_best"])
    test_best.append(["Clock Path", HOLD_VIOLATION_STR, TOTAL_HOLD_VIOLATION_STR, NUM_HOLD_VIO_STR])

    i = 0
    for line in qor_report:
        rtn = line.find("Scenario")
        if rtn != -1:
            rtn = line.find('func_slow')
            if rtn != -1:
                func_slow.append([qor_report[i+1].split()[3], qor_report[i+2].split()[3], qor_report[i+3].split()[3], qor_report[i+4].split()[4],
                                   qor_report[i+2].split()[3], qor_report[i+3].split()[3], qor_report[i+4].split()[4]])
            rtn = line.find('func_worst')
            if rtn != -1:
                func_worst.append([qor_report[i+1].split()[3], qor_report[i+2].split()[3], qor_report[i+3].split()[3], qor_report[i+4].split()[4]])
            rtn = line.find('func_best')
            if rtn != -1:
                func_best.append([qor_report[i+1].split()[3], qor_report[i+2].split()[3], qor_report[i+3].split()[3], qor_report[i+4].split()[4]])
            rtn = line.find('test_worst')
            if rtn != -1:
                test_worst.append([qor_report[i+1].split()[3], qor_report[i+2].split()[3], qor_report[i+3].split()[3], qor_report[i+4].split()[4]])
            rtn = line.find('test_best')
            if rtn != -1:
                test_best.append([qor_report[i+1].split()[3], qor_report[i+2].split()[3], qor_report[i+3].split()[3], qor_report[i+4].split()[4]])
        i += 1

    # Add stage variable to top of list.
    qor_report = []
    qor_report.append(["STAGE:", stage])
    # Not all scenarios may be present in the report. Don't append all scenario variables 
    # if they aren't present in the report.
    minimum_rows = 3
    if len(func_slow) > minimum_rows:
        for row in func_slow:
            qor_report.append(row)
    if len(func_worst) > minimum_rows:
        for row in func_worst:
            qor_report.append(row)
    if len(func_best) > minimum_rows:
        for row in func_best:
            qor_report.append(row)
    if len(test_worst) > minimum_rows:
        for row in test_worst:
            qor_report.append(row)
    if len(test_best) > minimum_rows:
        for row in test_best:
            qor_report.append(row)


    return qor_report


def format_qor_data_syn(qor_report, stage):
    """
    Function to make the data easier to read 
    for CSV/text format.

    input: qor_report: list containing items to be organized.
    input: stage: string of current stage being processed.

    """
    qor_report_temp = []
    qor_report_temp.append(["Timing Path Group", WNS_STR, TOTAL_NEG_SLACK_STR,
                            NUM_VIO_PTH_STR, HOLD_VIOLATION_STR, TOTAL_HOLD_VIOLATION_STR,
                            NUM_HOLD_VIO_STR])
    report_row = []
    for line in qor_report:
        line = line.strip("'")
        rtn = line.find("Timing Path Group")
        if rtn != -1:
            report_row = []
            report_row.append(line.split()[3])
        rtn = line.find(WNS_STR)
        if rtn != -1:
            report_row.append(line.split()[3])
        rtn = line.find(TOTAL_NEG_SLACK_STR)
        if rtn != -1:
            report_row.append(line.split()[3])
        rtn = line.find(NUM_VIO_PTH_STR)
        if rtn != -1:
            report_row.append(line.split()[4])
        rtn = line.find(HOLD_VIOLATION_STR)
        if rtn != -1:
            report_row.append(line.split()[3])
        rtn = line.find(TOTAL_HOLD_VIOLATION_STR)
        if rtn != -1:
            report_row.append(line.split()[3])
        rtn = line.find(NUM_HOLD_VIO_STR)
        if rtn != -1:
            report_row.append(line.split()[4])
            report_row = pd.DataFrame(report_row)
            report_row = report_row.transpose()
            report_row = report_row.values.tolist()
            qor_report_temp.append(report_row)

    qor_report = qor_report_temp
    
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
            rtn = line.find('func_slow')
            if rtn != -1:
                for k in range(2,12):
                    rtn = qor_report[i+k].find(WNS_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(TOTAL_NEG_SLACK_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(NUM_VIO_PTH_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(HOLD_VIOLATION_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(TOTAL_HOLD_VIOLATION_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(NUM_HOLD_VIO_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
            rtn = line.find('func_worst')
            if rtn != -1:
                for k in range(2,12):
                    rtn = qor_report[i+k].find(WNS_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(TOTAL_NEG_SLACK_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(NUM_VIO_PTH_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
            rtn = line.find('func_best')
            if rtn != -1:
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
            rtn = line.find('test_worst')
            if rtn != -1:
                for k in range(2,12):
                    rtn = qor_report[i+k].find(WNS_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(TOTAL_NEG_SLACK_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
                    rtn = qor_report[i+k].find(NUM_VIO_PTH_STR)
                    if rtn != -1:
                        qor_report_temp.append(qor_report[i+k])
            rtn = line.find('test_best')
            if rtn != -1:
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
    clock_qor.append([['STAGE:', stage]])
    for line in qor_report:
        rtn = line.find("Summary Reporting for Corner")
        if rtn != -1:
            k = 0
            clock_qor.append([[line]])
            clock_qor.append([['Clock Group', 'Attrs','Sinks','Levels','Clock Repeater Count',
                    'Clock Repeater Area', 'Clock Stdcell Area', 'Max Latency',
                    'Global Skew', 'Trans DRC Count', 'Cap DRC Count']])
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
        print("FILE NOT FOUND: " + file_path)
        return ""

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
        print("FILE NOT FOUND: " + file_path)
        return ""

    return qor_report


def write_qor_to_csv(top_design, reports, file_type):
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
        + '_reports_parsed.csv'
    with open(file_path, 'w') as csvfile:
        qor_writer = csv.writer(csvfile)
        for report in reports:
            for row in report:
                if type(row[0]) is list:
                    qor_writer.writerow(row[0])
                elif row is not None:
                    qor_writer.writerow(row)
    print("CSV file generated at path: " + file_path)


def write_data_to_text(top_design, reports, file_type):
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
        + '_report_text.txt'
    with open(file_path, 'w') as txtfile:
        for stage in reports:
            for row in stage:
                if row is not None:
                    for val in row:
                        if type(val) is str:
                            txtfile.write(val.ljust(ALIGN_LENGTH))
                        elif type(val) is list:
                            for element in val:
                                txtfile.write(element.ljust(ALIGN_LENGTH))
                        else:
                            txtfile.write(" ".ljust(ALIGN_LENGTH))
                    txtfile.write('\n')
    print("text file generated at path: " + file_path)
