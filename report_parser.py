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

import pandas as pd
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


        reports = []
        # Iterate through all stages of synopsys flow.
        for stage in sp.STAGES:

            # Create file path and read the file.
            to_open = top_design + "." + stage + ".qor.rpt"
            qor_report = sp.read_file_syn(to_open)
            # Error checking
            if qor_report == 1:
                return

            # Get all important values from qor report.
            timing_paths = sp.get_timing_paths(qor_report)
            wns_times = sp.get_wns(qor_report)
            tns_times = sp.get_tns(qor_report)
            worst_hold_vio = sp.get_worst_hold_violation(qor_report)
            hold_times = sp.get_hold_times(qor_report)

            # Read clock_qor report.
            to_open = top_design + "." + stage + ".clock_qor.rpt"
            print("Parsing file " + to_open)
            clock_qor = sp.read_file_syn(to_open)

            # Parse and format the clock_qor report.
            clock_qor = sp.parse_clock_qor(clock_qor)
            clock_qor = sp.format_clock_qor_data(clock_qor, timing_paths)

            # Prepend labels to data.
            current_stage = ["Stage: " + stage]
            timing_paths.insert(0, " ")
            wns_times.insert(0, "WNS Setup")
            tns_times.insert(0, "TNS Setup")
            worst_hold_vio.insert(0, "WNS Hold")
            hold_times.insert(0, "TNS Hold")

            # Prepend labels to data, and transpose the list so
            # data remains in proper order.
            clock_qor.insert(0, sp.COLUMN_LABELS_CLOCK_QOR)

            clock_qor = sp.transpose_data(clock_qor)    # transpose data for viewability.

            # Combine all the data together.
            report_qor = [current_stage, timing_paths, wns_times, tns_times,
                          worst_hold_vio, hold_times]
            for row in clock_qor:
                report_qor.append(row)

            # Transpose the data for viewability.
            report_qor = pd.DataFrame(report_qor)
            report_qor = report_qor.transpose()
            report_qor = report_qor.values.tolist()

            reports.append(report_qor)

        # Write results to CSV file and text file.
        sp.write_qor_to_csv(top_design, reports, "syn")
        sp.write_data_to_text(top_design, reports, "syn")

        reports = []
        # Iterate through all stages of synopsys flow.
        for stage in sp.STAGES:

            # Create file path and read the file.
            to_open = top_design + "." + stage + ".qor.rpt"
            qor_report = sp.read_file_apr(to_open)
            # Error checking
            if qor_report == 1:
                return

            # Get all important values from qor report.
            timing_paths = sp.get_timing_paths(qor_report)
            wns_times = sp.get_wns(qor_report)
            tns_times = sp.get_tns(qor_report)
            worst_hold_vio = sp.get_worst_hold_violation(qor_report)
            hold_times = sp.get_hold_times(qor_report)

            # Read clock_qor report.
            to_open = top_design + "." + stage + ".clock_qor.rpt"
            print("Parsing file " + to_open)
            clock_qor = sp.read_file_apr(to_open)

            # Parse and format the clock_qor report.
            clock_qor = sp.parse_clock_qor(clock_qor)
            clock_qor = sp.format_clock_qor_data(clock_qor, timing_paths)

            # Prepend labels to data.
            current_stage = ["Stage: " + stage]
            timing_paths.insert(0, " ")
            wns_times.insert(0, "WNS Setup")
            tns_times.insert(0, "TNS Setup")
            worst_hold_vio.insert(0, "WNS Hold")
            hold_times.insert(0, "TNS Hold")

            # Prepend labels to data, and transpose the list so
            # data remains in proper order.
            clock_qor.insert(0, sp.COLUMN_LABELS_CLOCK_QOR)

            clock_qor = sp.transpose_data(clock_qor)    # transpose data for viewability.

            # Combine all the data together.
            report_qor = [current_stage, timing_paths, wns_times, tns_times,
                          worst_hold_vio, hold_times]
            for row in clock_qor:
                report_qor.append(row)

            # Transpose the data for viewability.
            report_qor = pd.DataFrame(report_qor)
            report_qor = report_qor.transpose()
            report_qor = report_qor.values.tolist()

            reports.append(report_qor)

        # Write results to CSV file and text file.
        sp.write_qor_to_csv(top_design, reports, "apr")
        sp.write_data_to_text(top_design, reports, "apr")

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
