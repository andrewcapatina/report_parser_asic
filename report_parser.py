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


        qor_reports = []
        clock_qor_reports = []
        # Only one stage in flow for DC shell. (/syn/reports/)
        stage = "dc"

        # Create file path and read the file.
        to_open = top_design + "." + stage + ".qor.rpt"
        qor_report = sp.read_file_syn(to_open)

        syn_qor = []
        # Parse report if it was found. 
        if qor_report != "":
            # Get all important values from qor report.
            qor_report = sp.get_qor_data(qor_report)

            # Make the data viewable.
            qor_report = sp.format_qor_data(qor_report, stage)

            qor_report.insert(0, ["Flow:", "syn"])

            qor_reports = []
            for row in qor_report:
                qor_reports.append([row])

            syn_qor = qor_reports

        qor_reports = []
        clock_qor_reports = []
        # Iterate through all stages of synopsys place and route flow.
        for stage in sp.STAGES:

            # Create file path and read the file.
            to_open = top_design + "." + stage + ".qor.rpt"
            qor_report = sp.read_file_apr(to_open)
            # Error checking. Skip parsing the file if it wasn't found. 
            if qor_report != "":

                # Get all important values from qor report.
                qor_report = sp.get_qor_data(qor_report)

                # Make the data viewable.
                qor_report = sp.format_qor_data(qor_report, stage)

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

        qor_reports.insert(0, [["Flow:", "apr"]])
        clock_qor_reports.insert(0, [["Flow:", "apr"]])

        for row in qor_reports:
            syn_qor.append(row)

        # Write results to CSV file and text file.
        sp.write_qor_to_csv(top_design, syn_qor, "qor")
        sp.write_data_to_text(top_design, syn_qor, "qor")

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
        # Add titles to columns before getting data.
        stages_data.append(cp.SUMMARY_COLUMNS)
        for stage in cp.STAGES:  # Iterate through stages of Cadence flow.

            # Create file path and read file.
            folder_path = FOLDER_READ_PATH + top_design + ".innovus" + "/"
            file_name = stage + ".summary"
            file_path = folder_path + file_name

            # Error checking
            report = cp.read_file(file_path)
            if report == 1:
                return

            # Parse report contents
            report_contents = cp.parse_report(report)

            # Organize data for viewability.
            stage_summary = cp.organize_data(report_contents)
            stage_summary.insert(0, stage)
            stages_data.append(stage_summary)

        # Write results to CSV file and text file.
        cp.write_data_to_csv(top_design, stages_data)
        cp.write_data_to_text(top_design, stages_data)


if __name__ == "__main__":
    main()
