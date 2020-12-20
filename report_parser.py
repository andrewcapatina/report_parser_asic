"""
    Andrew Capatina
    5/12/2020

    Description:
    This is the top level file of the project. Repsonsible
    for prompting the user and calling the functions
    to generate appropriate reports.


"""

import cadence_parser as cp
import synopsys_parser as sp

import sys

FOLDER_READ_PATH = "reports/"       # Location of reports to be parsed.
FOLDER_WRITE_PATH = "outputs/"      # Location of the output parsed file.

ASIC_TOOLS = ["synopsys", "cadence"]    # Set of tools that generates reports.

def main():
    """
    Runs task of selecting which tool we are
    parsing reports from.
    """
    print("Welcome to ASIC tool Report Parser.")
    print("Please type which tool has generated the reports.")
    print("Options are: " + ASIC_TOOLS[0] + ", " + ASIC_TOOLS[1])

    # Version dependency for getting user input. 
    if sys.version_info[0] < 3:
        tool_option = raw_input()
    else:
        tool_option = input()
    # Checking if user selected synopsys tools
    if tool_option == ASIC_TOOLS[0]:
        print("Selected synopsys tools.")
        print("Current reports available for parsing:")
        print("- .qor files")
        print("- .clock_qor files")
        if sys.version_info[0] < 3:
            top_design = raw_input("Please enter the design name.\n")
        else:
            top_design = input("Please enter the design name\n")

	# Variable containing the qor report.
        qor_reports = []	
	# Iterate over flows for dc_shell. 
        dc_stage = ["dc", "dct"]
        qor_reports = []
	# This portion of the code will parse the 
	# .qor files under /syn for synthesis 
	# and physical synthesis flows. 
        for stage in dc_stage:
            # Create file name and read the file.
            to_open = top_design + "." + stage + ".qor.rpt"
            qor_report = sp.read_file_syn(to_open)

            # Parse report if it was found. 
            if qor_report != "":

                # Make the data viewable.
                qor_report = sp.format_qor_data_syn(qor_report, stage)

                # Add flow and stage label.
                qor_report.insert(0, ["FLOW:", "syn"])
                qor_report.insert(1, ["STAGE:", stage])

		# Append the reports to the variable containing 
		# the entire collection. 
                for row in qor_report:
                    qor_reports.append([row])

	# Assign the parsed file to a new variable.
        syn_qor = qor_reports

        qor_reports = []
        clock_qor_reports = []
	# This portion of the code will parse 
	# files under /apr for Automatic Place &
	# Route flows (APR). 
	# The current files parsed here are .qor and 
	# .clock_qor reports.
        for stage in sp.APR_STAGES:

            # Create file name and read the file.
            to_open = top_design + "." + stage + ".qor.rpt"
            qor_report = sp.read_file_apr(to_open)
            # Error checking. Skip parsing the file if it wasn't found. 
            if qor_report != "":

                # This function extracts data from
		# the qor_report.
                qor_report = sp.get_qor_data(qor_report)
		
                # Make the extracted data viewable.
                qor_report = sp.format_qor_data_apr(qor_report, stage)

                # Add report for this stage in a list saved.
                qor_reports.append(qor_report)

            # Read clock_qor report.
            to_open = top_design + "." + stage + ".clock_qor.rpt"
            clock_qor = sp.read_file_apr(to_open)
            # Error checking. Skip parsing the file if it wasn't found. 
            if clock_qor != "":

                # Parse and format the clock_qor report.
                clock_qor = sp.parse_clock_qor(clock_qor, stage)

                # Add report for this stage to the list of reports. 
                clock_qor_reports.append(clock_qor)

	
	# Label indicating data extracted from APR flow.
	if clock_qor_reports:
	        clock_qor_reports.insert(0, [["FLOW:", "apr"]])

        for row in qor_reports:
            syn_qor.append(row)

	if syn_qor:
        	# Write results to CSV file and text file.
        	sp.write_qor_to_csv(top_design, syn_qor, "qor")
        	sp.write_data_to_text(top_design, syn_qor, "qor")

	if clock_qor_reports:
        	sp.write_qor_to_csv(top_design, clock_qor_reports, "clock_qor")
        	sp.write_data_to_text(top_design, clock_qor_reports, "clock_qor")


    # Checking if user selected Cadence tools.
    if tool_option == ASIC_TOOLS[1]:
        print("Selected cadence tools.")
        print("Current reports available for parsing:")
        print("- .summary files")
        if sys.version_info[0] < 3:
            top_design = raw_input("Please enter the design name.\n")
        else:
            top_design = input("Please enter the design name.\n")
        stages_data = []
        for stage in cp.STAGES:  # Iterate through stages of Cadence flow.

            # Create file path and read file.
            folder_path = FOLDER_READ_PATH + top_design + ".innovus" + "/"
            file_name = stage + ".summary"
            file_path = folder_path + file_name

            report = cp.read_file(file_path)

	    if report:
		    # Parse report contents
		    report_contents = cp.parse_report(report)

		    # Organize data for viewability.
		    stage_summary = cp.organize_data(report_contents)
		    stage_summary.insert(0, stage)
		    stages_data.append(stage_summary)
	# Check if any data was actually collected.
	# If not, don't write to the files. 
	if stages_data:
		# Add titles to columns before getting data.
		stages_data.insert(0, cp.SUMMARY_COLUMNS)

		# Write results to CSV file and text file.
		cp.write_data_to_csv(top_design, stages_data)
		cp.write_data_to_text(top_design, stages_data)


if __name__ == "__main__":
    main()
