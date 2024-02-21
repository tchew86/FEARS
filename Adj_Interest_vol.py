from datetime import date, timedelta
from functools import partial
from time import sleep
from calendar import monthrange
import pandas as pd
from pytrends.exceptions import ResponseError
from pytrends.request import TrendReq
import os


def get_last_date_of_month(year: int, month: int) -> date:
    """Given a year and a month returns an instance of the date class
    containing the last day of the corresponding month.

    Source: https://stackoverflow.com/questions/42950/get-last-day-of-the-month-in-python
    """
    return date(year, month, monthrange(year, month)[1])


def convert_dates_to_timeframe(start: date, stop: date) -> str:
    """Given two dates, returns a stringified version of the interval between
    the two dates which is used to retrieve data for a specific time frame
    from Google Trends.
    """
    return f"{start.strftime('%Y-%m-%d')} {stop.strftime('%Y-%m-%d')}"


def _fetch_data(pytrends, build_payload, timeframe: str) -> pd.DataFrame:
    """Attempts to fecth data and retries in case of a ResponseError."""
    attempts, fetched = 0, False
    while not fetched:
        try:
            build_payload(timeframe=timeframe)
        except ResponseError as err:
            print(err)
            print(f'Trying again in {60 + 5 * attempts} seconds.')
            sleep(60 + 5 * attempts)
            attempts += 1
            if attempts > 3:
                print('Failed after 3 attemps, abort fetching.')
                break
        else:
            fetched = True
    return pytrends.interest_over_time()

def get_daily_data(word: str,
                   start_year: int,
                   start_mon: int,
                   stop_year: int,
                   stop_mon: int,
                   geo: str = 'US',
                   verbose: bool = True,
                   wait_time: float = 5.0,
                   cache=None) -> pd.DataFrame:

    # Set up start and stop dates
    start_date = date(start_year, start_mon, 1)
    stop_date = get_last_date_of_month(stop_year, stop_mon)

    # Start pytrends for US region outside the loop
    pytrends = TrendReq(hl='en-US', tz=360)
    # Initialize build_payload with the word we need data for
    build_payload = partial(pytrends.build_payload,
                            kw_list=[word], cat=0, geo=geo, gprop='')

    # Obtain monthly data for all months in years [start_year, stop_year]
    if cache is None or 'monthly' not in cache:
        monthly = _fetch_data(pytrends, build_payload,
                             convert_dates_to_timeframe(start_date, stop_date))
        cache['monthly'] = monthly
    else:
        monthly = cache['monthly']

    # Get daily data, month by month
    results = {}
    last_successful_month = None  # Track the last successful month retrieved
    consecutive_errors = 0  # Track consecutive 429 errors

    current = start_date if 'last_successful_month' not in cache else cache['last_successful_month']
    while current < stop_date:
        # Re-initialize TrendReq instance if there's an error
        pytrends = TrendReq(hl='en-US', tz=360)
        build_payload = partial(pytrends.build_payload,
                                kw_list=[word], cat=0, geo=geo, gprop='')

        last_date_of_month = get_last_date_of_month(current.year, current.month)
        timeframe = convert_dates_to_timeframe(current, last_date_of_month)
        if verbose:
            print(f'{word}:{timeframe}')

        try:
            if timeframe not in cache:
                results[current] = _fetch_data(pytrends, build_payload, timeframe)
                cache[timeframe] = results[current]
            else:
                results[current] = cache[timeframe]

        except ResponseError as err:
            print(err)
            consecutive_errors += 1
            if consecutive_errors % 4 == 0:  # Check for every 4 consecutive errors
                print(f'Trying again in 300 seconds after {consecutive_errors} consecutive 429 errors.')
                sleep(300)  # Sleep for 300 seconds after every 4 consecutive errors
            else:
                print(f'Trying again in 60 seconds.')
                sleep(60)  # Sleep for 60 seconds for normal consecutive errors

            # Set the last successful month to the previous one before the error occurred
            if last_successful_month:
                current = last_successful_month
            continue

        cache['last_successful_month'] = current  # Update the last successful month
        last_successful_month = current  # Update last_successful_month for potential future errors
        current = last_date_of_month + timedelta(days=1)
        sleep(wait_time)  # don't go too fast or Google will send 429s

    daily = pd.concat(results.values()).drop(columns=['isPartial'])
    complete = daily.join(monthly, lsuffix='_unscaled', rsuffix='_monthly')

    # Scale daily data by monthly weights so the data is comparable
    complete[f'{word}_monthly'].ffill(inplace=True)  # fill NaN values
    complete['scale'] = complete[f'{word}_monthly'] / 100
    complete[word] = complete[f'{word}_unscaled'] * complete.scale

    return complete


import pickle

# Function to save cache to file
def save_cache(cache, filename='cache.pkl'):
    with open(filename, 'wb') as file:
        pickle.dump(cache, file)

# Function to load cache from file
def load_cache(filename='cache.pkl'):
    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}

def merge_csv_files(keywords):
    all_data = pd.DataFrame()
    for keyword in keywords:
        file_path = f'data_{keyword}.csv'  # Adjusted to match your file naming convention
        if os.path.exists(file_path):
            keyword_data = pd.read_csv(file_path, index_col=0)  # Assuming first column is the date/index
            all_data = pd.concat([all_data, keyword_data], axis=1)
        else:
            print(f"File not found for keyword: {keyword}")
    return all_data

if __name__ == "__main__":
    # Adjust the parameters accordingly for your research time frame
    start_year = 2004
    start_month = 1
    stop_year = 2011
    stop_month = 12

    # List of keywords to process
    final_keywords_df = pd.read_csv('/Users/riccardodjordjevic/Desktop/Excel/final_keywords.csv')
    keywords = final_keywords_df['Keywords'].tolist()

    gathered_keywords_count = 0
    for word in keywords:
        # Load existing cache or create an empty one for each keyword
        data_cache = load_cache()

        # Fetch the data for the current keyword using cache
        data = get_daily_data(word, start_year, start_month, stop_year, stop_month, wait_time=10.0,
                              cache=data_cache)

        # Check if the data is gathered for the full timeframe before saving and deleting cache
        last_date_fetched = data.index[-1].date()
        stop_date = get_last_date_of_month(stop_year, stop_month)
        if last_date_fetched == stop_date:
            # Save the 'data' DataFrame as a CSV file
            data.to_csv(f'data_{word}.csv')
            print(f'{word} data saved as csv')
            gathered_keywords_count += 1

            progress_percentage = (gathered_keywords_count / len(keywords)) * 100

            # Print the progress with the percentage
            print(f"{gathered_keywords_count} keywords gathered out of {len(keywords)} total keywords "
                  f"({progress_percentage:.2f}% complete)")

            # Delete the cache
            data_cache.clear()
            save_cache(data_cache)
        else:
            print(f"Data gathering incomplete for {word}. Not saving CSV or deleting cache.")

        # Display the fetched data
        print(data.head())

        # Sleep for 60 seconds before processing the next keyword
        if word != keywords[-1]:  # Skip sleep on the last iteration
            print(f"Sleeping for 60 seconds before processing the next keyword...")
            sleep(60)

    merged_data = merge_csv_files(keywords)

    # Saving the merged data into a new CSV file
    merged_data.to_csv('merged_interest_over_time.csv')
    print("Merged data saved as 'merged_interest_over_time.csv'")
