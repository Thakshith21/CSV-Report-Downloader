#!/usr/bin/env python3
import cgi
import cgitb
import csv
from datetime import datetime
import os
import logging

cgitb.enable()

# Print HTTP headers
print("Content-Type: text/html\n")

# Get form data
form = cgi.FieldStorage()
frontend_start_date = form.getvalue("start_date")
frontend_end_date = form.getvalue("end_date")
frontend_category = form.getvalue("category")

# Parse the dates
try:
    start_date = datetime.strptime(frontend_start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(frontend_end_date, "%Y-%m-%d").date()
except ValueError:
    print("Invalid date format provided. Please enter dates in YYYY-MM-DD format.")
    exit(1)

# Ensure start_date is not later than end_date
if start_date > end_date:
    print("Error: Start date cannot be later than end date.")
    exit(1)

# Log form data
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info(f"Start Date: {start_date}, End Date: {end_date}, Category: {frontend_category}")

# Input and output folder paths
input_folder = "/var/www/html/thakshith/pmock/txt"  # Replace with your folder path
output_folder = "/var/www/html/thakshith/pmock/output1"  # Replace with your folder path

# Function to create CSV for the specified date range
def create_csv_for_date_range(start_date, end_date, report_name="date_range_report.csv"):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Prepare the path for the report
    report_path = os.path.join(output_folder, report_name)

    # Check if the input folder exists
    if not os.path.exists(input_folder):
        logging.error(f"Input folder not found: {input_folder}")
        return None

    # Open the report file for writing
    with open(report_path, 'w', newline='', encoding='utf-8') as report_file:
        csv_writer = csv.writer(report_file)

        # Write header row
        csv_writer.writerow(["Timestamp", "UserID", "Event", "Type", "Category", "Details"])

        # Process each file in the input folder
        for file_name in os.listdir(input_folder):
            # Check if the file ends with .txt and matches the date format
            if file_name.endswith(".txt") and len(file_name.split('.')[0]) == 10:
                file_date_str = file_name.split('.')[0]  # Extract the date part

                # Parse the date string from the file name
                try:
                    file_date = datetime.strptime(file_date_str, "%Y-%m-%d").date()
                except ValueError:
                    logging.warning(f"Skipping invalid file date: {file_date_str}")
                    continue  # Skip invalid date files

                # Check if the file date is within the specified range
                if start_date <= file_date <= end_date:
                    input_file_path = os.path.join(input_folder, file_name)

                    # Log file processing
                    logging.info(f"Processing file: {file_name}")

                    # Read and write rows from the file
                    with open(input_file_path, 'r', encoding='utf-8') as txt_file:
                        for line in txt_file:
                            row = line.strip().split("##")
                            # Check if the row has at least 6 parts before writing to CSV
                            if len(row) >= 6:
                                csv_writer.writerow(row)
                            else:
                                logging.warning(f"Skipping invalid row: {row}")
                else:
                    logging.info(f"Skipping file {file_name} because it is outside the date range.")


    logging.info(f"Date range report generated: {report_path}")
    return report_path

# Function to filter CSV based on category
def filter_data_by_category(csv_file_path, category, filtered_report_name="filtered_category_report.csv"):
    filtered_report_path = os.path.join(output_folder, filtered_report_name)

    # Check if the input csv exists
    if not os.path.exists(csv_file_path):
        logging.error(f"CSV file not found: {csv_file_path}")
        return None

    with open(filtered_report_path, 'w', newline='', encoding='utf-8') as filtered_csv_file:
        csv_writer = csv.writer(filtered_csv_file)

        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Read header if available
            try:
                headers = next(csv_reader)
                csv_writer.writerow(headers)
            except StopIteration:
                logging.warning("Empty file, no header to process.")
                return filtered_report_path  # Can be considered successful since the file has been created

            for row in csv_reader:
                # Check if the list is long enough to get element 4 and if the category matches
                if len(row) > 4 and row[4].strip().lower() == category.strip().lower():
                    csv_writer.writerow(row)

    logging.info(f"Filtered report based on category '{category}' generated: {filtered_report_path}")
    return filtered_report_path

# Function to remove duplicate UserIDs and combine their unique details
def remove_duplicate_user_ids(csv_file_path, deduplicated_report_name="deduplicated_report.csv"):
    deduplicated_report_path = os.path.join(output_folder, deduplicated_report_name)

    # Check if the input csv exists
    if not os.path.exists(csv_file_path):
        logging.error(f"CSV file not found: {csv_file_path}")
        return None

    main_dict = {}

    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)

        # Read header
        headers = next(csv_reader, None)

        for row in csv_reader:
            if len(row) >= 6:
                user_id = row[1]
                event = row[2].strip()
                event_type = row[3].strip()
                category = row[4].strip()
                detail = row[5].strip()

                # If UserID already exists in the dictionary
                if user_id in main_dict:
                    existing_entry = main_dict[user_id]
                    # Combine unique event values
                    if event not in existing_entry["Event"]:
                        if existing_entry["Event"]:
                            existing_entry["Event"] += f", {event}"
                        else:
                            existing_entry["Event"] = event

                    # Combine unique type values
                    if event_type not in existing_entry["Type"]:
                        if existing_entry["Type"]:
                            existing_entry["Type"] += f", {event_type}"
                        else:
                            existing_entry["Type"] = event_type

                    # Combine unique category values
                    if category not in existing_entry["Category"]:
                        if existing_entry["Category"]:
                            existing_entry["Category"] += f", {category}"
                        else:
                            existing_entry["Category"] = category

                    # Combine unique detail values
                    if detail not in existing_entry["Details"]:
                        if existing_entry["Details"]:
                            existing_entry["Details"] += f", {detail}"
                        else:
                            existing_entry["Details"] = detail
                else:
                    # Add a new entry for the UserID
                    main_dict[user_id] = {
                        "Timestamp": row[0],
                        "Event": event,
                        "Type": event_type,
                        "Category": category,
                        "Details": detail
                    }

    # Write deduplicated data to a new CSV file
    with open(deduplicated_report_path, 'w', newline='', encoding='utf-8') as deduplicated_csv_file:
        csv_writer = csv.writer(deduplicated_csv_file)

        # Write headers
        if headers:
            csv_writer.writerow(headers)

        # Write rows from the main dictionary
        for user_id, details in main_dict.items():
            csv_writer.writerow([
                details["Timestamp"],
                user_id,
                f"[{details['Event']}]",  # Format Event as a list
                f"[{details['Type']}]",  # Format Type as a list
 details["Category"],
                details["Details"]
            ])

    logging.info(f"Deduplicated report generated: {deduplicated_report_path}")
    return deduplicated_report_path

# Step 1: Create CSV for the given date range
date_range_csv = create_csv_for_date_range(start_date, end_date)

if date_range_csv:  # Check if the date range csv was generated successfully
    # Step 2: Filter the generated CSV by category
    filtered_csv = filter_data_by_category(date_range_csv, frontend_category)
    if filtered_csv:
        # Step 3: Remove duplicate UserIDs and combine details
        deduplicated_csv = remove_duplicate_user_ids(filtered_csv)

        if not deduplicated_csv:
            logging.error("Deduplication was not successful. Check the log for further information.")
    else:
        logging.error("Filtering data was not successful. Check the log for further information.")
else:
    logging.error("CSV generation was not successful. Check the log for further information.")

if deduplicated_csv:
     print(f'<a href="http://dev.oliveboard.in/thakshith/pmock/output1/deduplicated_report.csv" target="_blank">Download the CSV</a><br>')
