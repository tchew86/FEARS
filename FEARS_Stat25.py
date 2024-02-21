import os
import pandas as pd
import numpy as np
from scipy.stats import mstats
import statsmodels.api as sm
from datetime import datetime

def merge_csv_columns(folder_path):
    filtered_df = pd.DataFrame()

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if file.endswith('.csv'):
            df = pd.read_csv(file_path)

            if df.shape[1] >= 6:
                filtered_df = pd.concat([filtered_df, df.iloc[:, 5]], axis=1)

    data_401k_path = os.path.join(folder_path, 'data_401k.csv')
    if os.path.exists(data_401k_path):
        data_401k_df = pd.read_csv(data_401k_path)
        if not data_401k_df.empty:
            filtered_df.insert(0, 'Dates', data_401k_df.iloc[:, 0])

    return filtered_df


def extract_keywords(folder_path):
    keywords = []

    for file in os.listdir(folder_path):
        if file.startswith('data_') and file.endswith('.csv'):
            keyword = file[len('data_'):-len('.csv')]
            keywords.append(keyword)

    return keywords


# Replace 'your_folder_path' with the path to your CSV files
folder_path = '/Users/riccardodjordjevic/Desktop/Google/csv'

# Call the functions and store their outputs
filtered_df = merge_csv_columns(folder_path)
keywords = extract_keywords(folder_path)

# Now, you can use 'merged_df' and 'keywords' in your broader script
print("Keywords:", keywords)
print("Merged DataFrame:")
print(filtered_df)

non_zero_counts = ((filtered_df != 0) | filtered_df.isna()).sum()

# Filter columns with at least 2571 non-zero observations
filtered_columns = non_zero_counts[non_zero_counts >= 1000].index

# Select the filtered columns
filtered_merged_all_df = filtered_df[filtered_columns]

# Display the number of non-zero observations per column
print("Number of non-zero observations per column:")
print(non_zero_counts)

# Display the filtered dataframe
print("\nFiltered DataFrame with columns having at least 1000 non-zero observations:")
print(filtered_merged_all_df)

def calculate_log_difference(column):
    # Add a small constant to avoid log of zero or negative values
    epsilon = 1e-10
    log_diff = np.log(column + epsilon) - np.log(column.shift(1) + epsilon)
    return log_diff

# Apply the log difference calculation to each column except the first
log_diff_df = filtered_merged_all_df.iloc[:, 1:].apply(calculate_log_difference, axis=0)

# Combine the results with the original DataFrame
result_df = pd.concat([filtered_merged_all_df.iloc[:, 0], log_diff_df], axis=1)

# Display the resulting DataFrame
print("\nDataFrame with natural log difference for each observation:")
print(result_df)

filtered_winsorized_df = result_df.copy()
#dates_column = filtered_df.iloc[:, 0]  # Store the dates column


for col in filtered_winsorized_df.columns:
    winsorized_values = mstats.winsorize(filtered_winsorized_df[col], limits=[0.025, 0.025])
    filtered_winsorized_df[col] = winsorized_values

# Add the dates column back to the DataFrame
#filtered_winsorized_df.insert(0, 'Dates', dates_column)

# Display the modified DataFrame with the date column added
print("\nwinsorized df:")
print(filtered_winsorized_df)

dates_column = filtered_df.iloc[:, 0]

def extract_date_info(date_series):
    dates = pd.to_datetime(date_series)
    return dates.dt.weekday, dates.dt.month

# Extract weekday and month information
filtered_winsorized_df['Weekday'], filtered_winsorized_df['Month'] = extract_date_info(filtered_winsorized_df['Dates'])

# Perform regression and store residuals for each column (except the first)
residuals_dict = {}
for col in filtered_winsorized_df.columns[1:]:
    X = pd.get_dummies(filtered_winsorized_df[['Weekday', 'Month']])
    X = sm.add_constant(X)  # Add a constant for intercept
    y = filtered_winsorized_df[col]

    model = sm.OLS(y, X).fit()
    residuals = model.resid

    std_dev = residuals.std()
    residuals = residuals / std_dev

    residuals_dict[col] = residuals

# Store residuals and add the dates column back in a new DataFrame
residuals_df = pd.DataFrame(residuals_dict)
residuals_df.insert(0, 'dates', dates_column)

# Display the residuals DataFrame with dates and divided values by standard deviation
print("\nDataFrame with residuals for each column divided by standard deviation:")
print(residuals_df)

residuals_df.to_excel('residuals.xlsx', index=False)

excel_file_path = '/Users/riccardodjordjevic/Desktop/CSV/SP500.xlsx'
sp = pd.read_excel(excel_file_path)

# Convert date format in the first column from 'dd/mm/yyyy' to 'yyyy-mm-dd'
#what am I supposed to write here? (maybe nothing)

# Set the first column as the index (assuming the first column is the date column)
sp.set_index(sp.columns[0], inplace=True)

start_date_ = pd.to_datetime('2004-01-01')
end_date_ = pd.to_datetime('2011-12-31')
filtered_sp = sp.loc[start_date_:end_date_]

print('S&P500 df')
print(filtered_sp)

# Rename the first column to 'dates' to match the column name in residuals_df
residuals_df['dates'] = pd.to_datetime(residuals_df['dates'])
filtered_sp.index = pd.to_datetime(filtered_sp.index)

# Merge based on the index (first column)
mrdf = pd.merge(residuals_df, filtered_sp, left_on='dates', right_index=True, how='inner')

# Print the merged DataFrame with residuals and additional columns from the Excel file
print("Merged DataFrame with residuals and additional columns:")
print(mrdf)

mrdf.to_excel('mrdf.xlsx', index=False)
# Define the list of columns to regress
columns_to_regress = residuals_df.columns[1:-2].tolist()

# Define the number of rolling regressions
num_regressions = 15

# Initialize a DataFrame to store the average t-statistics
average_t_stats_df = pd.DataFrame(index=columns_to_regress, columns=range(num_regressions))

# Perform the rolling regressions
for n in range(num_regressions):
    # Define the end row for this regression
    end_row = 1950 - 130 * n

    # Select the data for the current regression
    data = mrdf.iloc[:end_row]

    # Initialize lists to store t-statistics for each column
    t_stats = []

    # Perform the regression for each column in columns_to_regress
    for column in columns_to_regress:
        X = sm.add_constant(data[column])
        y = data['return']
        model = sm.OLS(y, X).fit()
        t_stat = model.tvalues[column]
        t_stats.append(t_stat)

    # Calculate the average t-statistics for this regression and store in the DataFrame
    average_t_stats_df[n] = t_stats

# Print or use the average_t_stats_df DataFrame for further analysis
print('results t_stat')
print(average_t_stats_df)
average_t_stats_df.to_excel('avg_tstat.xlsx', index=False)

smallest_lists = {}

# Iterate over each column in average_t_stats_df
for n in range(num_regressions):
    # Get the column name (e.g., '3_smallest_0')
    col_name = f'30_smallest_{n}'

    # Get the 30 smallest values and their corresponding row names for the current column
    smallest_values = average_t_stats_df.iloc[:, n].nsmallest(25)

    # Store the row names in the dictionary
    smallest_lists[col_name] = smallest_values.index.tolist()

# Print the 15 lists
for col_name, row_names in smallest_lists.items():
    print(f'{col_name}: {row_names}')

# Create a list to store filtered DataFrames
filtered_dfs = []
total_rows = len(mrdf)
rows_per_split = total_rows // 16

# Split the DataFrame into 16 smaller DataFrames
for i in range(16):
    start_row = total_rows - (i + 1) * rows_per_split
    end_row = total_rows - i * rows_per_split
    split_name = f'split_{i}'
    split_data = mrdf.iloc[start_row:end_row]

    print(f'First 10 rows of {split_name} before filtering:')
    print(split_data.head(10))
    print('-' * 40)

    # Filter the split based on the 3_smallest_{n} for the current split
    if i < num_regressions:  # Ensure you have a corresponding '3_smallest_{i}' for this split
        split_keywords = smallest_lists[f'30_smallest_{i}']
        filtered_split_name = f'filtered_split_{i}'

        # Create a DataFrame with the same columns as split_data but with NaN values
        filtered_split_data = pd.DataFrame(index=split_data.index, columns=split_data.columns)

        # Set values for selected columns
        filtered_split_data[split_keywords] = split_data[split_keywords]

        filtered_dfs.append(filtered_split_data)

        # Print the first 10 rows of the filtered split
        print(f'First 10 rows of {filtered_split_name}:')
        print(filtered_split_data.head(10))
        print('-' * 40)


# Concatenate the filtered DataFrames vertically in decreasing order of i
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Assuming 'df' is defined before this script and 'filtered_dfs' is a list of DataFrames

# Your existing code to create 'merged_df'
merged_df = pd.concat(filtered_dfs[::-1], ignore_index=True)

# Add a new column to calculate the average of each row
merged_df['row_average25'] = merged_df.mean(axis=1)

# Extract the first column without the first 139 rows
first_column_df = mrdf.iloc[:, 0].iloc[130:]

# Insert the first column as the first column of 'merged_df'
merged_df.insert(0, 'date', first_column_df.reset_index(drop=True))

# Calculate the average of every 10 values of 'row_average'
merged_df['smoothed_row_average'] = merged_df['row_average25'].rolling(window=10).mean()

# Save 'merged_df' as an Excel file
output_excel_path = '/Users/riccardodjordjevic/Desktop/pythonProject2/merged_dataframe_with_first_column25.xlsx'
merged_df.to_excel(output_excel_path, index=False)

# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 6))

# Plot the smoothed line graph
line, = ax.plot(merged_df['date'], merged_df['smoothed_row_average'], marker='o', linestyle='-', color='b')

# Customize the plot for better readability
ax.set_title('Smoothed FEARS index Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Smoothed FEARS index')
ax.tick_params(axis='x', rotation=45, labelright=True)  # Rotate x-axis labels for better readability
ax.grid(True)

# Add a slider for smoothing adjustment
ax_slider = plt.axes([0.1, 0.01, 0.65, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Smoothing Level', 0, 80, valinit=10)

# Function to update the plot based on the slider value
def update(val):
    window_size = int(slider.val)
    merged_df['smoothed_row_average'] = merged_df['row_average25'].rolling(window=window_size).mean()
    line.set_ydata(merged_df['smoothed_row_average'])
    fig.canvas.draw_idle()

# Attach the update function to the slider
slider.on_changed(update)

# Show the plot
plt.subplots_adjust(bottom=0.15)
plt.show()