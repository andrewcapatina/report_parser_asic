"""
    Andrew Capatina
    5/9/2020
    Description:
        This file has modules for parsing qor report and clock_qor
        report of Cadence tools. Creates a CSV list of all the important
        data to be printed.
"""
import csv
import gzip as gz
import pandas as pd


# Modify this parameter to increase 
# number of paths displayed for full_clock timing files.
NUM_PATHS_FULL_CLK = 5

ALIGN_LENGTH = 25  # Used for aligning words in text file.
FOLDER_READ_PATH = "../syn/reports/"       # Location of reports to be parsed.
FOLDER_WRITE_PATH = "outputs/"      # Location of the output parsed file.
STAGES = ['place', 'postcts', 'postcts_hold', 'route', 'route_hold']  # Stages for flow.
STAGES_full_clock = ['place', 'cts', 'postcts', 'route']  # Stages for flow.
# Columns in a summary timing report. Modify if Cadence changes reporting.
SUMMARY_COLUMNS = ['Stage', 'reg2reg_WNS/TNS/Vio', 'in2reg_WNS/TNS/Vio',
                   'reg2out_WNS/TNS/Vio', 'in2out_WNS/TNS/Vio']
# Strings used to search for important content. Modify if reporting changes.
WNS_STR = "WNS"
TNS_STR = "TNS"
VIO_PATH_STR = "Violating Paths"


def read_gz_file(file_path):
    """
        Function to read file and return the whole file.
        input: file_path - file path to qor files.
        output: report - file contents returned.
    """
    try:
        with gz.open(file_path + ".gz", 'r') as gp:
            report_temp = gp.readlines()
    except:
        print("File path {0} not found.".format(file_path))
        return ""

    # Converts bytes object to string. 
    report = []
    for row in report_temp:
        row = row.decode('utf-8')
        report.append(row)

    return report


def organize_data(report_contents):
    """
           Function to organize the contents of the report
           into a single list so that it can be displayed in a
           CSV file.

           input: report_contents: list of lists containing information
           parsed from timing reports.

           output: stage_summary: list containing timing information
           for current stage.
    """
    # Convert to pandas array, transpose, and convert back to list.
    report_contents = pd.DataFrame(report_contents)
    report_contents = report_contents.transpose()
    report_contents = report_contents.values.tolist()

    stage_summary = []
    # Iterate through report and concatenate relevant data.
    for row in report_contents:
        mode_sum = ""
        for val in row:
            mode_sum = mode_sum + str(val) + " "
        mode_sum = mode_sum.replace(' ', '/')
        stage_summary.append(mode_sum)

    return stage_summary


def parse_report(report):
    """
        Function to parse a QOR report. Essentially finds useful
        string and removes unneeded characters.

        input: qor_report: list containing contents of report.
        output: report_contents: list containing parsed data.
    """
    # Check if the input parameter is empty.
    if not report:
	return 
    report_contents = []
    for line in report:
        line = line.replace('|', '')
        line = line.replace(':', '')
        rtn = line.find(WNS_STR)
        rtn_2 = line.find(TNS_STR)
        rtn_3 = line.find(VIO_PATH_STR)
        if rtn != -1 or rtn_2 != -1 \
        or rtn_3 != -1:
            line = line.split()
            line = line[3:7]
            report_contents.append(line)
            continue

    return report_contents

def parse_clock_path_report(report, stage):
   """
	Function to extract data from timing report
	containing the full clock paths.

	input: report: List. Contains the full report.
	input: stage: current stage in APR flow.
   """
   i = 0		# Tracks which line is being parsed.
   num_paths = ""	# Contains number of paths in report.

   # This contains the worst slack times in order.
   # Update the global variable to increase the number
   # of slack times collected.
   slack_list = []

   # This for loop gathers all the data needed from the report.
   for line in report:
	# Save the number of paths from the report.
	if line.find("-max_paths") != -1:
		num_paths = int(line.split()[1])
		if num_paths < NUM_PATHS_FULL_CLK:
			raise Exception("Can't gather more paths than available in full_clock file. Decrease NUM_PATHS_FULL_CLK variable.")
	if line.find("slack") != -1:
		# Start collecting after report title/introduction.
		if i > 20:
			# Get the third element becuase that's the slack time for the path.
			path_slack = float(line.split()[2])

			if len(slack_list) < NUM_PATHS_FULL_CLK:
				slack_list.append(path_slack)

				sorted(slack_list, reverse=True)	
			elif len(slack_list) < slack_list[NUM_PATHS_FULL_CLK - 1]:
				slack_list.pop(NUM_PATHS_FULL_CLK - 1)
				slack_list.append(path_slack)

				sorted(slack_list, reverse=True)	

	i = i + 1   # Increment as we iterate line by line.
   
   label_str = "Worst slack times for stage " + stage
   slack_list.insert(0, label_str)
	
   return slack_list


def write_full_clock_data_txt(top_design, slack_list):
    """
	Function to write the worst failing slack times
	from full_clock timing files to a text file.

	input: top_design: str. design being evaluated.
	input: slack_list: list. Contains worst failing times for each stage of APR flow. 
    """
    file_path = FOLDER_WRITE_PATH + top_design + ".full_clock_worst_slack_times" + ".txt" 

    with open(file_path, 'w') as txtfile:

	for line in slack_list:
		txtfile.write(str(line) + '\n')	
    print("text file generated at path: " + file_path)
    txtfile.close()

def write_data_to_csv(top_design, stages_data):
    """
        Function to print all of the parsed data to a CSV file.

        input: top_design: design currently being worked on.
        input: stages data: list of lists containing timing information.
    """
    file_path = FOLDER_WRITE_PATH + top_design + '_stages_summary.csv'
    with open(file_path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for row in stages_data:
            writer.writerow(row)
    print("CSV file generated at path: " + file_path)


def write_data_to_text(top_design, stages_data):
    """
        Function that writes all the report 
        summaries to a text file.

        https://stackoverflow.com/questions/16796709/align-columns-in-a-text-file

        input: top_design: string indicating design name.
        input: reports: list of lists containing report data.
    """
    file_path = FOLDER_WRITE_PATH + top_design + '_report_text.txt'
    with open(file_path, 'w') as txtfile:
        for stage in stages_data:
            for val in stage:
                if val is not None:
                    txtfile.write(val.ljust(ALIGN_LENGTH))
                else:
                    txtfile.write(" ".ljust(ALIGN_LENGTH))
            txtfile.write('\n')
    print("text file generated at path: " + file_path)


