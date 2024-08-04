# Sentiment Metrics in Finance: documentation

## Table of Contents
- I. Introduction
- II. Installation and Requirements 
- III. Usage and Troubleshooting
- IV. Contact


## I. Introduction

This document outlines the technical framework for the algorithm that generates the FEARS index, a metric for investor sentiment that offers an alternative to conventional assessment methods such as surveys or proxies. Starting from the work of Da et al. (2015), the FEARS index tackles the issues both firms and researchers encounter with investor sentiment's impact on asset mispricing and the issues involved in its measurement.

The documentation includes a **Usage and Troubleshooting** section, which mentions best practices on how to make the various algorithms work. At the end of the documentation is possible to find contact information. Launched as part of the Honours Programme at the Utrecht School of Economics (USE), this initiative strives to duplicate the findings of "The Sum of all FEARS: Investor Sentiment and Asset Prices" (Da et al., 2015), aiming to extend the analysis beyond its initial period of 2004-2011. The primary goal is to engineer an algorithm that autonomously calculates the FEARS index daily, thereby broadening the arsenal of tools for measuring investor and household sentiment.

A comprehensive report detailing the theoretical foundation of this code and various observations, titled `Sentiment Metrics in Finance - Report.pdf`, is available in the repository. This ensures access to contextual information. It's crucial to acknowledge that this report was composed before the complete acquisition of data necessary for the index, thereby focusing on insights from preliminary testing of the FEARS index.

## II. installations and Requirements

install the requirements by running the following line in your terminal. Use pip3 instead of pip if you are a Mac user. 
```installation
pip install -r requirements.txt
```
**Other Requirements**
- Stable internet connection. The code still works in case of a short lack of internet connection (i.e. a modem restart). However, the code has not been tested in case of prolonged lack in internet connection.
- The latest version of your favourite Python interpreter.
- Python 3.9 or more recent.

## III. Usage and Troubleshooting

This section has been divided into **Quick Start**, to be read to ensure proper working of the code and understand the various parameters, and **Troubleshooting**, to be read to understand the possible errors that might take place. Note that it is important to read this section in conjunction with the `Sentiment Metrics in Finance - Report.pdf` file in this repository to better understand the econometrics model behind the FEARS index. Note that to achieve a correct construction of the FEARS index it is important to run the algorithms in the same order as they are reported in this documentation.

## a) Quick Start

Before even starting to use Python, it is important to select the list of primitive keywords from the `inquirerbasic.xls` file. The file can be downloaded from the [Harvard IV-4 Dictionary and the Lasswell Value Dictionary](https://inquirer.sites.fas.harvard.edu/). Select an Excel Pivot Table when they are marked with `@Econ` or `ECON`, and additionally are also marked with `Ngtv`, `Negativ`, `Positiv`, or `Pstv`.

### 1. Keywords_Gather.py

This script needs to be used first as it gathers the list of the top 10 related queries per each primitive keyword.

- The first step is to manually download the `.csv` files containing the top 10 related queries from [Google Trends](https://trends.google.com/trends/). Download all the files into a separate folder.
  - At the top of the page, select 'United States' as the location, set the time frame that you want to look at, and leave the last field as 'Web Search'. The original paper (Da et al. 2015) works on the 2004-2011 period.
  - It is possible to download the file at the bottom right of the page.
- Paste the folder path with all the downloaded .csv files at line 28 of the code:
  ```python
  tester_folder_path = "path/to/your/folder"
  ```
- Set at line 47 the path to the file containing the list of top 10 related queries. The file name must be `final_keywords.csv`
- Select with a Pivot table only the queries that have economic relevance. (i.e. if there are the words ‘economic depression’ and ‘postpartum depression’, only the former will be kept). Save These Keywords in a new file named `Broad_economic_Keywords.csv`. This process is highly arbitrary since it is possible to select every keyword that might be related to economic output (i.e. expensive cars, luxury houses, etc.), or only those related to investor sentiment (i.e. recession, chapter 11, inflation, etc.). In this repository is possible to find the file `Broad_economic_Keywords.csv` containing the queries with a broad economic and financial meaning that we selected.


### 2. Adj_Interest_vol.py

This is the second algorithm that needs to be used code, and it gathers the adjusted search volume for each of the Top 10 related queries.

- Set at lines 157-170 the timeframe that the script needs to look at. After each variable indicate the number of the month or of the year. the example reports the timeframe 1st January 2004 to 31st December 2011.
 ```commandline
  start_year = 2004
  start_month = 1
  stop_year = 2011
  stop_month = 12
  ```
- Set at line 163 the path of the `Broad_economic_Keywords.csv` file that has been created as output by the previous algorithm.
 ```commandline
    final_keywords_df = pd.read_csv('path/to/Broad_economic_Keywords.csv`)
  ```
- The Search Volume is saved in different csv files for different keywords. Gather all the csv files manually in a new single folder.

NB: the execution of this code is rather lengthy. While using a single IP the script was able to group daily search volume for just above 400 words, for the 8 years, in just above three weeks, which means that it is possible to build an up-to-date FEARS index in just over six months. The process might accelerate if used in combination with  

### 3. FEARS_Stat25.py, FEARS_Stat30.py, FEARS_Stat35.py

- At line 41 set the same folder path where you have gathered all the `.csv` files containing the interest over time for the various keywords. The previous script should save the files in the same folder as the script. In theory, the script should work if you assign to this folder the same path as the script, however, we strongly advise moving all the `.csv` files to a new folder.
```python
folder_path = '/path/to/the/csv/folder'
```

- In this script, there might be an error given at line 20 (not expected to happen frequently). This is caused by the fact that the algorithm uses the date column from the 'data_401k' data frame when merging all the `.csv` files. Therefore, if this keyword is not present among the related queries, its data frame will not be present either. To fix this error is possible to switch 'data_401k' with any other related query that has been gathered.
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
This command line comes from `FEARS_Stat30.py`, where from each rolling regression **30** keywords with the most negative t-statistics are selected. In `FEARS_Stat25.py` **25** keywords with the most negative t-statistics are selected. In `FEARS_Stat35.py` **35** keywords with the most negative t-statistics are selected. This leads to slightly different scripts and different calculations of the FEARS index. More information on this can be found in the original paper of Da et al. (2015), or in the `Sentiment Metrics in Finance - Report.pdf` file.
The three different algorithms also return three different output `.xlsx` files with different FEARS values. The names of the output files are reported in the table below

**Algorithm and output file names**

| Algorithm name  | n. keywords selected/rolling regression | FEARS index column | output file name                          |
|-----------------|-----------------------------------------|--------------------|-------------------------------------------|
| FEARS_Stat25.py | 25                                      | row_average25      | merged_dataframe_with_first_column25.xlsx |
| FEARS_Stat30.py | 30                                      | row_average30      | merged_dataframe_with_first_column30.xlsx |
| FEARS_Stat35.py | 35                                      | row_average35      | merged_dataframe_with_first_column35.xlsx |

NB: the FEARS index can be found in the columns `row_average25`, `row_average30`, `row_average35` (depending on how many keywords are selected per rolling regression) of each output file. The column `smoothed_row_average` of each output data frame does not report the actual FEARS index, but an average of the index for multiple days. The purpose of the smoothed column is to make the graph of the FEARS index more readable by taking the average FEARS values for multiple days. The number of days that are considered to calculate a single data point can be regulated through a slider at the bottom of the plotted graph.  

- During the execution, the algorithms will print 15 lists named `30_smallests_{n}` with n(0:14) even though it might be selecting 25 or 35 keywords. Inside these lists, it is possible to find the keywords that have been selected based on each rolling regression. Consult `Sentiment Metrics in Finance - Report.pdf` for the theoretical background.

### 4. generate_markdown_table.py

This is the last script needed for the proper engineering of the FEARS index. It compares the main statistical parameters of the FEARS index built by Da et al. with the on constructed with the previous three scripts.
- to make the code work it is necessary to assign to the variables `excel_file1` the path of `merged_dataframe_with_first_column25.xlsx`, to `excel_file2` the path of `merged_dataframe_with_first_column30.xlsx`, and to `excel_file3` the path of `merged_dataframe_with_first_column35.xlsx`, as reported in the following code chunk
```commandline
excel_file1 = '/path/to/merged_dataframe_with_first_column25.xlsx'
excel_file2 = '/path/to/merged_dataframe_with_first_column30.xlsx'
excel_file3 = '/path/to/merged_dataframe_with_first_column35.xlsx'
```
- The data frame of the original paper is retrieved through a web link. However, we have also uploaded it as `Original_Data.csv`.
- This algorithm also generates an Excel Table which is useful to visualise the original and new FEARS 30 index. Between lines 65 and 73 4 additional columns are created by taking the rolling average and smoothing the index to make it more comprehensible. It is possible to regulate the size of the rolling window.
```commandline
new_df['ORIGINAL FEARS 30 - 60 days smoothing'] = original_df['fears30'].rolling(window=60).mean()

new_df['NEW FEARS 30 - 60 days smoothing'] = df2['row_average30'].rolling(window=60).mean()

new_df['ORIGINAL FEARS 30 - 120 days smoothing'] = original_df['fears30'].rolling(window=120).mean()

new_df['NEW FEARS 30 - 120 days smoothing'] = df2['row_average30'].rolling(window=120).mean()
```

Below is possible to find the **comparison statistics** tables of the FEARS index from the original paper and the one calculated with the previous algorithms. The analysis should be taken with caution as it has not been possible to require information on all keywords, yet. `generate_markdown_table.py` will have to be run another time when information on every related query will be gathered.

#### comparison statistics:

| Statistic | Original Dataset (fears25) | Compare Dataset (row_average25) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.37 | 0.25 |
| Min | -2.83 | -1.06 |
| 25% | -0.17 | -0.17 |
| 50% | -0.01 | -0.04 |
| 75% | 0.16 | 0.13 |
| Max | 3.57 | 1.34 |
| Skewness | 1.78 | 0.53 |
| Kurtosis | 19.88 | 1.26 |
| Correlation Coefficient | | 0.02 |

| Statistic | Original Dataset (fears30) | Compare Dataset (row_average30) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.35 | 0.24 |
| Min | -2.55 | -1.17 |
| 25% | -0.15 | -0.16 |
| 50% | -0.02 | -0.04 |
| 75% | 0.13 | 0.12 |
| Max | 3.19 | 1.27 |
| Skewness | 1.87 | 0.58 |
| Kurtosis | 18.31 | 1.54 |
| Correlation Coefficient | | 0.03 |

| Statistic | Original Dataset (fears35) | Compare Dataset (row_average35) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.34 | 0.24 |
| Min | -2.29 | -1.16 |
| 25% | -0.15 | -0.16 |
| 50% | -0.02 | -0.04 |
| 75% | 0.13 | 0.11 |
| Max | 2.92 | 1.27 |
| Skewness | 1.92 | 0.59 |
| Kurtosis | 17.57 | 1.63 |
| Correlation Coefficient | | 0.02 |

#### comparison statistics (after gathering data on 829 words):

| Statistic | Original Dataset (fears25) | Compare Dataset (row_average25) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.37 | 0.24 |
| Min | -2.83 | -1.01 |
| 25% | -0.17 | -0.15 |
| 50% | -0.01 | -0.02 |
| 75% | 0.16 | 0.13 |
| Max | 3.57 | 1.42 |
| Skewness | 1.78 | 0.24 |
| Kurtosis | 19.88 | 1.27 |
| Correlation Coefficient | | 0.04 |

| Statistic | Original Dataset (fears30) | Compare Dataset (row_average30) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.35 | 0.23 |
| Min | -2.55 | -1.03 |
| 25% | -0.15 | -0.15 |
| 50% | -0.02 | -0.02 |
| 75% | 0.13 | 0.13 |
| Max | 3.19 | 1.35 |
| Skewness | 1.87 | 0.35 |
| Kurtosis | 18.31 | 1.62 |
| Correlation Coefficient | | 0.04 |

| Statistic | Original Dataset (fears35) | Compare Dataset (row_average35) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.34 | 0.22 |
| Min | -2.29 | -0.88 |
| 25% | -0.15 | -0.15 |
| 50% | -0.02 | -0.02 |
| 75% | 0.13 | 0.11 |
| Max | 2.92 | 1.25 |
| Skewness | 1.92 | 0.43 |
| Kurtosis | 17.57 | 1.56 |
| Correlation Coefficient | | 0.03 |

#### comparison statistics (after gathering data on 970 words, of which 960 are used because 10 words do not have scaled data):

| Statistic | Original Dataset (fears25) | Compare Dataset (row_average25) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.37 | 0.24 |
| Min | -2.83 | -1.01 |
| 25% | -0.17 | -0.15 |
| 50% | -0.01 | -0.02 |
| 75% | 0.16 | 0.13 |
| Max | 3.57 | 1.42 |
| Skewness | 1.78 | 0.24 |
| Kurtosis | 19.88 | 1.27 |
| Correlation Coefficient | | 0.04 |

| Statistic | Original Dataset (fears30) | Compare Dataset (row_average30) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.35 | 0.23 |
| Min | -2.55 | -1.03 |
| 25% | -0.15 | -0.15 |
| 50% | -0.02 | -0.02 |
| 75% | 0.13 | 0.13 |
| Max | 3.19 | 1.35 |
| Skewness | 1.87 | 0.35 |
| Kurtosis | 18.31 | 1.62 |
| Correlation Coefficient | | 0.04 |

| Statistic | Original Dataset (fears35) | Compare Dataset (row_average35) |
|-----------|-----------|-----------|
| Mean | 0.00 | -0.01 |
| Std | 0.34 | 0.22 |
| Min | -2.29 | -0.88 |
| 25% | -0.15 | -0.15 |
| 50% | -0.02 | -0.02 |
| 75% | 0.13 | 0.11 |
| Max | 2.92 | 1.25 |
| Skewness | 1.92 | 0.43 |
| Kurtosis | 17.57 | 1.56 |
| Correlation Coefficient | | 0.03 |

### OLS regression results

S&P500 return is the dependent variable. Independent variables are FEARS Index (30 keywords selected, variable name 'row_average30),
ADS Index (variable name 'ADS_Index'), VIX Index (variable name 'OPEN'), daily difference of EPU Index (variable name 'change_index). Every independent variable is both contemporaneous and up to five lags.

<img width="624" alt="Screenshot 2024-08-04 at 14 59 03" src="https://github.com/user-attachments/assets/a69b7dde-0b5c-4f0d-a2d6-0927f86c96c9">


<img width="696" alt="Screenshot 2024-08-04 at 14 52 51" src="https://github.com/user-attachments/assets/bdebb9a4-44eb-4240-9ade-d716d211eb09">


Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 6.61e+03. This might indicate that there are
strong multicollinearity or other numerical problems.

The file used to calculate the regression is uploaded as `regressor.py` however we strongly advise being careful with this file as it has presented various bugs while adding and cleaning the data, therefore it might not work properly. 


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
