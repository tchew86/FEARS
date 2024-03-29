import pandas as pd
from scipy.stats import kurtosis, skew
import matplotlib.pyplot as plt

# Load the original dataset from the CSV file
original_df = pd.read_csv('https://www3.nd.edu/~zda/fears_post_20140512.csv')

# Define a function to calculate the statistics
def get_stats(df, column_name):
    stats = df[column_name].describe()
    stats['Skewness'] = skew(df[column_name])
    stats['Kurtosis'] = kurtosis(df[column_name])
    return stats

# Compare the specified columns from each dataset and generate Markdown table
def compare_and_generate_markdown(original_df, compare_df, original_column, compare_column):
    original_stats = get_stats(original_df, original_column)
    compare_stats = get_stats(compare_df, compare_column)

    # Calculate the correlation coefficient
    correlation = original_df[original_column].corr(compare_df[compare_column])

    markdown_table = "| Statistic | Original Dataset (" + original_column + ") | Compare Dataset (" + compare_column + ") |\n"
    markdown_table += "|-----------|-----------|-----------|\n"
    for stat in ['mean', 'std', 'min', '25%', '50%', '75%', 'max', 'Skewness', 'Kurtosis']:
        markdown_table += f"| {stat.title()} | {original_stats[stat]:.2f} | {compare_stats[stat]:.2f} |\n"
    markdown_table += f"| Correlation Coefficient | | {correlation:.2f} |\n"

    return markdown_table

# Placeholder for the actual Excel file paths
excel_file1 = '/Users/riccardodjordjevic/Desktop/pythonProject2/merged_dataframe_with_first_column25.xlsx'
excel_file2 = '/Users/riccardodjordjevic/Desktop/pythonProject2/merged_dataframe_with_first_column30.xlsx'
excel_file3 = '/Users/riccardodjordjevic/Desktop/pythonProject2/merged_dataframe_with_first_column35.xlsx'

# Load the datasets from Excel files
df1 = pd.read_excel(excel_file1)
df2 = pd.read_excel(excel_file2)
df3 = pd.read_excel(excel_file3)

# Perform comparisons and generate Markdown tables
markdown_table1 = compare_and_generate_markdown(original_df, df1, 'fears25', 'row_average25')
markdown_table2 = compare_and_generate_markdown(original_df, df2, 'fears30', 'row_average30')
markdown_table3 = compare_and_generate_markdown(original_df, df3, 'fears35', 'row_average35')

# Combine the Markdown tables into one
combined_markdown_table = markdown_table1 + "\n" + markdown_table2 + "\n" + markdown_table3

# Print the combined Markdown table
print(combined_markdown_table)

# To write the combined Markdown table to a .md file
with open('combined_comparison_statistics.md', 'w') as md_file:
    md_file.write(combined_markdown_table)

# Plotting df2 and original_df['fears30']
new_df = pd.DataFrame({
    'Date': df2.iloc[:, 0],  # First column of df2
    'ORIGINAL FEARS 30': original_df['fears30'],  # fears30 column of original_df
    'NEW FEARS 30': df2['row_average30'],  # row_average30 column of df2
})

# Add a fourth column for smoothed 'Second Column' (rolling average of 30 rows)

new_df['ORIGINAL FEARS 30 - 60 days smoothing'] = original_df['fears30'].rolling(window=60).mean()

# Add a fifth column for smoothed 'Third Column' (rolling average of 30 rows)
new_df['NEW FEARS 30 - 60 days smoothing'] = df2['row_average30'].rolling(window=60).mean()

new_df['ORIGINAL FEARS 30 - 120 days smoothing'] = original_df['fears30'].rolling(window=120).mean()

# Add a fifth column for smoothed 'Third Column' (rolling average of 30 rows)
new_df['NEW FEARS 30 - 120 days smoothing'] = df2['row_average30'].rolling(window=120).mean()


# Print the new DataFrame
print(new_df)

# To write the new DataFrame to a .csv file
new_df.to_excel('new_dataframe_with_smoothing.xlsx', index=False)
