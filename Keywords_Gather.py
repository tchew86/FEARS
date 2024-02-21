import pandas as pd
import os


def process_csv_files(folder_path):
    processed_data = []

    # List all CSV files in the folder
    file_names = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    for file_name in file_names:
        full_path = os.path.join(folder_path, file_name)
        try:
            # Read the CSV file, specifying the rows
            df = pd.read_csv(full_path, skiprows=4, nrows=10, header=None)

            # Add the items in the first column to the processed data
            processed_data.extend(df.iloc[:, 0].tolist())
        except FileNotFoundError:
            print(f"File not found: {full_path}")
        except Exception as e:
            print(f"An error occurred with file {full_path}: {e}")

    return processed_data


# Specify the path to the 'Tester' folder on your desktop
tester_folder_path = '/Users/riccardodjordjevic/Desktop/Tester'

final_data_list = process_csv_files(tester_folder_path)

# Print the length of the initial list
print("Length of the initial list:", len(final_data_list))

print(final_data_list)
# Remove duplicates from the list
final_data_list = list(set(final_data_list))

# Print the length of the list after removing duplicates
print("Length of the list after removing duplicates:", len(final_data_list))

# The final data is now stored in final_data_list
print(final_data_list)

final_df = pd.DataFrame(final_data_list, columns=["Keywords"])

output_csv_file = '/Users/riccardodjordjevic/Desktop/Excel/final_keywords.csv'
final_df.to_csv(output_csv_file, index=False)

print("Length of the list after removing duplicates:", len(final_data_list))
print("Final data exported to:", output_csv_file)