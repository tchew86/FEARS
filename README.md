# Sentiment Metrics in Finance: documentation

## Table of Contents
- I. Introduction
- II. Installation and Requirements 
- III. Usage and Troubleshooting
- IV. Contact


## I. Introduction

This document outlines the technical framework for the algorithm that generates the FEARS index, a metric for investor sentiment that offers an alternative to conventional assessment methods such as surveys or proxies. Starting from the work of Da et al. (2015), the FEARS index tackles the issues both firms and researchers encounter with investor sentiment's impact on asset mispricing and the issues involved in its measurement.

The documentation includes a **Usage and Troubleshooting** section, which mentions that best practices on how to make the various algorithms work. At the end of the documentation is possible to find contact information. Launched as part of the Honours Programme at the Utrecht School of Economics (USE), this initiative strives to duplicates the findings of "The Sum of all FEARS: Investor Sentiment and Asset Prices" (Da et al., 2015), aiming to extend the analysis beyond its initial period of 2004-2011. The primary goal is to engineer an algorithm that autonomously calculates the FEARS index daily, thereby broadening the arsenal of tools for measuring investor and household sentiment.

A comprehensive report detailing the theoretical foundation of this code and various observations, titled `Sentiment Metrics in Finance - Report.pdf`, is available in the repository. This ensures access to contextual information. It's crucial to acknowledge that this report was composed before the complete acquisition of data necessary for the index, thereby focusing on insights from preliminary testing of the FEARS index.

## II. installations and Requirements

install the requirements by running the following line in your terminal. Use pip3 instead of pip is you are a Mac user. 
```installation
pip install -r requirements.txt
```
**Other Requirements**
- Stable internet connection. The code still works in case of a short lack of internet connection (i.e. a modem restart). However, the code has not been tested in case of prolonged lacks in internet connection.
- The latest version of your favourite Python interpreter.
- Python 3.9 or more recent.

## III. Usage and Troubleshooting

This section has been divided into **Quick Start**, to be read to ensure proper working of the code and understand the various parameters, and **Troubleshooting**, to be read to understand the possible errors that might take place. Note that it is important to read this section in conjunction with the `Sentiment Metrics in Finance - Report.pdf` file in this repository to better understand the econometrics model behind the FEARS index. Note that to achieve a correct construction of the FEARS index it is important to run the algorithms in the same order as they are reported in this documentation.

## a) Quick Start

Before even starting to use Python, it is important to select the list of primitive keywords from the `inquirerbasic.xls` file. The file can be downloaded from the [Harvard IV-4 Dictionary and the Lasswell Value Dictionary](https://inquirer.sites.fas.harvard.edu/). Select an Excel Pivot Table when they are marked with `@Econ` or `ECON`, and additionally are also marked with `Ngtv`, `Negativ`, `Positiv`, or `Pstv`.

### 1. Keywords_Gather.py (`test_55`)

This script needs to be used first as it gathers the list of the top 10 related queries per each primitive keyword.

- The first step is to manually download the `.csv` files containing the top 10 related queries from [Google Trends](https://trends.google.com/trends/). Download all the files into a separate folder.
  - At the top of the page, select 'United States' as the location, set the time frame that you want to look at, and leave the last field as 'Web Search'. The original paper (Da et al. 2015) works on the 2004-2011 period.
  - It is possible to download the file at the bottom right of the page.
- Paste the folder path with all the downloaded .csv files at line 28 of the code:
  ```python
  tester_folder_path = "path/to/your/folder"
  ```
- Set at line 47 the path to the file containing the list of top 10 related queries. The file name must be `final_keywords.csv`

### 2. Adj_Interest_vol.py (test_62)

This is the second algorithm that needs to be used code, and it gathers the adjusted search volume for each of the Top 10 related queries.

- Set at lines 157-170 the timeframe that the script needs to look at. After each variable indicate the number of the month or of the year. the example reports the timeframe 1st January 2004 to 31st December 2011.
 ```commandline
  start_year = 2004
  start_month = 1
  stop_year = 2011
  stop_month = 12
  ```
- Set at line 163 the path of the `final_keywords.csv` file that has been created as output by the previous algorithm.
 ```commandline
    final_keywords_df = pd.read_csv('path/to/final_keywords.csv')
  ```
- The Search Volume is saved in different csv file for different keywords. Gather all the csv file manually in a new single folder.

NB: the execution of this code is rather lengthy. While using a single IP the script was able to group daily search volume for just above 400 words, for the 8 years, in just above three weeks, which means that it is possible to build an up-to-date FEARS index in just above six months. The process might accelerate if used in combination with  

### 3. FEARS_Stat25.py (test69), FEARS_Stat30.py (test68), FEARS_Stat35.py (test70)

- At line 41 set the same folder path where you have gathered all the `.csv` files containing the interest over time for teh various keywords. The previous script should save the files in the same folder of the script. In theory the scrit should work if you assign to this folder the same path of the script, however we strongly advise to move al the `.csv` files in a new folder.
```python
folder_path = '/path/to/the/csv/folder'
```

- since this documentation has been written before the search volume of every keyword has been gathered, the algorithm still misses a key step. At line 67 a User interface should be integrated in the code which asks the user which keywords should be kept. This step is import to remove all the queries tha are not related to economic and nor to finance (i.e. if there are the words ‘economic depression’ and ‘postpartum depression’, only the former will be kept). The authors in the original paper are left with a list of 118 queries after starting from 622 queries that have at least 1000 observations of daily data. However, these numbers might change since Google's algorithms also changed in the meanwhile and this might have lead to a slightly different list of related queries.
- In this script there might be an error given at line 20 (not expected to happen frequently). This is caused by the fact that the algorithm uses the date column from the 'data_401k' data frame when merging all the `.csv` files. Therefore, if this keyword is not present among the related queries, its dataframe will noe be present either. To fix this error is possible to switch 'data_401k' with any other related query that has been gathered.
```commandline
    data_401k_path = os.path.join(folder_path, 'data_401k.csv')
   ```
- Another factor to pay attention to is the number of daily observations that we consider relevant 
```commandline
filtered_columns = non_zero_counts[non_zero_counts >= 1000].index
```

As you might have noticed in this section of the **Usage and TroubleShooting** we refer at the same time to three different algorithms. Namely, FEARS_Stat25.py, FEARS_Stat30.py and FEARS_Stat35.py. We do so because the algorithms are identical, except for a small difference at line 205.
```commandline
    smallest_values = average_t_stats_df.iloc[:, n].nsmallest(30)
```
This command line comes from `FEARS_Stat30.py`, where from each rolling regressions **30** keywords with the most negative t-statistics are selected. In `FEARS_Stat25.py` **25** keywords with the most negative t-statistics are selected. In `FEARS_Stat35.py` **35** keywords with the most negative t-statistics are selected. This leads to slightly different script and different calculations of the FEARS index. More information on this can be found in the original paper of Da et al. (2015), or in the `Sentiment Metrics in Finance - Report.pdf` file.
The three different algorithms also return three different output `.xlsx` files with different FEARS values. The names of the output files are reported in the table below

**Algorithm and output file names**

| Algorithm name  | n. keywords selected/rolling regression | FEARS index column | output file name                          |
|-----------------|-----------------------------------------|--------------------|-------------------------------------------|
| FEARS_Stat25.py | 25                                      | row_average25      | merged_dataframe_with_first_column25.xlsx |
| FEARS_Stat30.py | 30                                      | row_average30      | merged_dataframe_with_first_column30.xlsx |
| FEARS_Stat35.py | 35                                      | row_average35      | merged_dataframe_with_first_column35.xlsx |

NB: the FEARS index can be found in the columns `row_average25`, `row_average30`, `row_average35` (depending on how many keywords are selected per rolling regression) of each output file. The column `smoothed_row_average` of each output data frame do not report the actual FEARS index, but an average of the index for multiple days. The purpose of the smoothed column is to make the graph of the FEARS index more readable by taking the average FEARS values for multiple days. The number of days that are considered to calculate a single data point can be regulated through a slider at the bottom of the plotted graph.  

### 4. generate_markdown_table.py

This is the last script of needed for a proper engineering of the FEARS index. It compares the main statistical parameters of the FEARS index built by Da et al. with the on constructed with the previous three scripts.
- to make the code work it is necessary to assign to the variables `excel_file1` the path of `merged_dataframe_with_first_column25.xlsx`, to `excel_file2` the path of `merged_dataframe_with_first_column30.xlsx`, and to `excel_file3` the path of `merged_dataframe_with_first_column35.xlsx`, as reported in the following code chunk
```commandline
excel_file1 = '/path/to/merged_dataframe_with_first_column25.xlsx'
excel_file2 = '/path/to/merged_dataframe_with_first_column30.xlsx'
excel_file3 = '/path/to/merged_dataframe_with_first_column35.xlsx'
```
- The data frame of the original paper is retrieved through a web link.

Below is possible to find the **comparison statistics** tables of the FEARS index from the original paper and the one calculated with the previous algorithms. The analysis should be taken with caution as it has not been possible to require information on all keywords, yet. `generate_markdown_table.py` will have to be run another time when information on every related query will be gathered.

#### comparison statistics:

| Statistic | Original Dataset (fears25) | Compare Dataset (row_average25) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.37 | 0.22 |
| Min | -2.83 | -1.13 |
| 25% | -0.17 | -0.15 |
| 50% | -0.01 | -0.02 |
| 75% | 0.16 | 0.11 |
| Max | 3.57 | 1.29 |
| Skewness | 1.78 | 0.18 |
| Kurtosis | 19.88 | 1.53 |

| Statistic | Original Dataset (fears30) | Compare Dataset (row_average30) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.35 | 0.21 |
| Min | -2.55 | -1.08 |
| 25% | -0.15 | -0.14 |
| 50% | -0.02 | -0.02 |
| 75% | 0.13 | 0.11 |
| Max | 3.19 | 1.21 |
| Skewness | 1.87 | 0.17 |
| Kurtosis | 18.31 | 1.84 |

| Statistic | Original Dataset (fears35) | Compare Dataset (row_average35) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.34 | 0.20 |
| Min | -2.29 | -1.28 |
| 25% | -0.15 | -0.14 |
| 50% | -0.02 | -0.02 |
| 75% | 0.13 | 0.11 |
| Max | 2.92 | 1.29 |
| Skewness | 1.92 | 0.26 |
| Kurtosis | 17.57 | 2.63 |

## b) Troubleshooting

If you encounter issues while running the code, particularly with its performance or execution, please consider the following potential solutions:

### Internet Connection Interruptions

- The code is designed to handle short disruptions in internet connectivity, such as those caused by brief electricity outages or modem restarts. However, prolonged loss of internet access may cause the code to cease functioning properly.

### Code Not Working on First Attempt

Should the code fail to execute correctly on the first attempt, try these steps in order:

1. **Create a New Script**: Copy the existing code into a new script file and execute this new script. This can sometimes resolve hidden issues related to the script environment.

2. **Restart IDLE**: Close and reopen the IDLE application. A fresh start can often clear any runtime errors or environmental issues.

3. **Restart Your Laptop**: If the above steps do not resolve the issue, a full restart of your laptop may be necessary. This can help reset your system's state.

4. **Performance Variability**: It is normal for the code to run faster overnight. This is due to lower competition for resources on the Google Trends Server, which imposes concurrency request limits. Running your scripts during off-peak hours can result in improved performance and faster execution times.

By following these troubleshooting steps, you should be able to resolve most issues encountered during the execution of the code.


## IV. Contact

- [Linkedin - Riccardo Djordjevic](https://www.linkedin.com/in/riccardo-djordjevic/)
- [riccardo.djordjevic@outlook.com](mailto:riccardo.djordjevic@outlook.com)