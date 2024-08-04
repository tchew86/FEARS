import pandas as pd

# Load the Excel and CSV files into dataframes
fears_df = pd.read_excel('merged_dataframe_with_first_column30.xlsx')
sp500_df = pd.read_excel('/Users/riccardodjordjevic/Desktop/CSV/SP500.xlsx')
ads_df = pd.read_excel('ADS.xlsx')
epu_df = pd.read_csv('EPU.csv')  # No date conversion needed
vix_df = pd.read_csv('VIX.csv')  # Date conversion needed

print("SP500")
print(sp500_df)

# Convert the date format in specific dataframes from Y-m-d to d/m/YYYY
def convert_dates(df):
    date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d').dt.strftime('%d/%m/%Y')
    return df

# Apply date conversion to specified dataframes
fears_df = convert_dates(fears_df)
sp500_df = convert_dates(sp500_df)
ads_df = convert_dates(ads_df)

# Convert the date format in vix_df from mm/dd/YYYY to dd/mm/YYYY
vix_df.iloc[:, 0] = pd.to_datetime(vix_df.iloc[:, 0], format='%m/%d/%Y').dt.strftime('%d/%m/%Y')
vix_df.iloc[:, 0] = vix_df.iloc[:, 0].astype(str)

# Convert the first column of each dataframe to a string
fears_df.iloc[:, 0] = fears_df.iloc[:, 0].astype(str)
sp500_df.iloc[:, 0] = sp500_df.iloc[:, 0].astype(str)
ads_df.iloc[:, 0] = ads_df.iloc[:, 0].astype(str)
epu_df.iloc[:, 0] = epu_df.iloc[:, 0].astype(str)
vix_df.iloc[:, 0] = vix_df.iloc[:, 0].astype(str)

print(ads_df)

# Concatenate dataframes on the first column
merged_df = pd.concat([fears_df.set_index(fears_df.columns[0]),
                       sp500_df.set_index(sp500_df.columns[0]),
                       ads_df.set_index(ads_df.columns[0]),
                       epu_df.set_index(epu_df.columns[0]),
                       vix_df.set_index(vix_df.columns[0])], axis=1, join='inner').reset_index()

# Display the final merged dataframe
print(merged_df)

desired_columns = ['date', 'row_average30', 'daily_policy_index',
                    'change_index', 'OPEN']
filtered_df = merged_df[desired_columns]


filtered_df02 = pd.concat([filtered_df.set_index(filtered_df.columns[0]),
                       ads_df.set_index(ads_df.columns[0])], axis=1, join='inner').reset_index()



filtered_df02.to_excel('reg.xlsx', index=False)

ret = ['date', 'return', '2day_return']
sp_ret = sp500_df[ret]

print(sp_ret)

filtered_df02 = pd.concat([filtered_df02.set_index(filtered_df02.columns[0]),
                       sp_ret.set_index(sp_ret.columns[0])], axis=1, join='inner').reset_index()

print(filtered_df02)
print(list(filtered_df02.columns))

import statsmodels.api as sm

# Create lagged features
def create_lagged_features(df, lags, cols):
    for col in cols:
        for lag in range(0, lags + 1):
            df[f'{col}_lag{lag}'] = df[col].shift(lag)
    return df

# Define lagging parameters
lags = 5
lag_columns = ['change_index', 'OPEN', 'ADS_Index', 'row_average30']


# Create lagged features
filtered_df_reg1 = create_lagged_features(filtered_df02, lags, lag_columns)

# Drop rows with NaN values created by lagging
filtered_df_reg1 = filtered_df_reg1.dropna()

# Define independent and dependent variables
X = filtered_df_reg1[['row_average30', 'change_index', 'OPEN', 'ADS_Index'] + [f'{col}_lag{lag}' for col in lag_columns for lag in range(1, lags + 1)]]
y = filtered_df_reg1['return']

# Add a constant (intercept) to the model
X = sm.add_constant(X)

# Fit the model
model = sm.OLS(y, X).fit()

# Print the summary
print(model.summary())

