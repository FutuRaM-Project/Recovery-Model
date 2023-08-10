'''
The goal of the script is to convert an Excel file
(which may contain multiple sheets) into individual CSV files, one for each sheet.:
Steps:
1. Load Excel file
2. Determine output directory
3. Iterate over sheets
4. csv creation
5. Completion message
'''
import openpyxl
import csv
import os

def xlsx_to_csvs(filename, output_folder = None):
    """
      This function splits an Excel (.xlsx) file into separate CSV files for each sheet.

      Parameters
      ----------
      filename : str
          The path to the xlsx file.
      output_folder : str, optional
          The path to the output folder where CSV files will be saved.
          If not provided, a folder named after the Excel file with `-split` appended will be used.

      Returns
      -------
      folder_name : str
          The name of the folder where the CSV files were created.
          :param output_folder:

      """
    # Step 1: Print a message indicating the start of the conversion process
    print(f'\n\n{"*" * 60}\n{"*" * 4} Splitting {os.path.basename(filename)} into CSV files {"*" * 4}\n{"*" * 60}')

    # Step 2: We should be able to handle potential exceptions,
    # like if the file is not found or if there is an issue during the CSV writing process.
    # Step 2: Attempt to set the path to the file and load the Excel workbook
    try:
        workbook = openpyxl.load_workbook(filename, data_only=True)
    except Exception as e:
        print(f"Error loading the Excel file: {e})")
        return

    # Step 3: Get the names of all sheets in the Excel workbook
    sheet_names = workbook.sheetnames
        # Step 3.1: Encourage users to rename default-named sheets
        default_sheet_names = [sheet_name for sheet_name in sheet_names if sheet_name.startswith('Sheet')]
        if default_sheet_names:
            print("\nEncouragement:")
            print("\nConsider renaming the following sheets to something more descriptive:")
            for sheet_name in default_sheet_names:
            sheet_number = sheet_names.index(sheet_name) + 1  # +1 because sheet indexing starts from 1
            print(f'Change name of Sheet number {sheet_number}: ***{sheet_name.upper()}***')
            print("\n")

    # Step 4: Determine the output folder's name
    folder_name =  output_folder or f'{os.path.splitext(filename)[0]}-split'
    os.makedirs(folder_name, exist_ok=True)

    # Step 5: Loop through each sheet to create corresponding CSV file(s)
    for sheet_name in sheet_names:
        worksheet = workbook[sheet_name]
        csv_file_path = os.path.join(folder_name, f'{sheet_name}.csv')

        # Step 5.1: Open the csv file for writing
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Step 5.2: Write the headers (first row) from the Excel sheet to the CSV file
            headers = [cell.value for cell in worksheet[1]]
            writer.writerow(headers)

            # Step 5.3: Write the data to the CSV file (check for different conditions)
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                # Skip rows with 'total' in the first cell or entirely empty rows
                if not row[0] or 'total' not in row[0].lower():
                    # Remove trailing None value if present
                    if row[-1] is None:
                        row = row[:-1]
                    writer.writerow(row)

        # Step 5.4: Find the last non-empty row
        last_row = worksheet.max_row
        while last_row > 1 and all(cell.value is None for cell in worksheet[last_row]):
            last_row -= 1

        # Step 5.5: Remove empty rows at the end of the CSV file
        with open(f'{folder_name}/{sheet_name}.csv', 'r+', newline='') as csvfile:
            data = csvfile.read().splitlines(True)
            csvfile.seek(0)
            csvfile.writelines(data[:last_row + 1]) # adding this +1 because last_row here is not None but slicing opeartion is end-exclusive
            csvfile.truncate()

    # Step 6: Print a completon message along with the names of sheets processed
    print(f'\nFiles were created in {folder_name}')
    print('\nSheets extracted:')
    for sheet_name in sheet_names: print(f'\t\t{sheet_name}')

    return folder_name