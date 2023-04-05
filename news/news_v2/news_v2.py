import pandas as pd
import time
import datetime
import json
import requests


def get_available():
    url = "https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=demo"
    stock_df = pd.read_csv(url)
    available = set(stock_df["symbol"])
    return available


def get_dates():
    start_date = "2022-03-01"
    end_date = "2023-03-31"
    month_start_dates = pd.date_range(start=start_date, end=end_date, freq="SMS")
    month_end_dates = pd.date_range(start=start_date, end=end_date, freq="SM")

    # create a list of tuples of (start date, end date)
    dates = []
    for start, end in zip(month_start_dates, month_end_dates):
        # add one day to start date to avoid overlapping date range
        if start.day == 15:
            start += datetime.timedelta(days=1)
        t = (start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
        dates.append(t)

    return dates


def get_stock_prices(available, dates, skipfirst: int):
    sp500_df = pd.read_csv("sp500.csv")
    api_key = "8VUOFOJS4BENDZG9"

    df_list = []  # to store stock price
    error_dict = {}  # to store error URL

    for index, company, symbol in sp500_df[["Company", "Symbol_modified"]].itertuples(index=True, name=None):
        count = index + 1
        if count <= skipfirst:
            continue
        print(f"Processing {count}-th symbol: {symbol}")
        if symbol not in available:
            print(f"The following symbol is not available: {symbol}")
            # log error in error dict
            error_dict[symbol] = "Not available"
            continue
        for start, end in dates:
            url = "https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
            # format url
            url += f"&tickers={symbol}"
            url += f"&topics=earnings"
            url += f"&time_from={start}T0000"
            url += f"&time_to={end}T2359"
            url += f"&sort=RELEVANCE"
            url += f"&limit=200"
            url += f"&apikey={api_key}"
            print(f"Pulling data from {start} to {end}")
            print(url)

            # retry for 10 times in case server is unavailable
            for i in range(0, 10):
                try:
                    r = requests.get(url)
                    data = r.json()
                    # 30 requests per minute so sleep 2 seconds between requests
                    time.sleep(2)
                except Exception as e:
                    print(e)
                    if i == 9:
                        raise
                    else:
                        continue
                break
            if "feed" not in data:
                # log error in error dict
                error_dict[url] = data
                print(f"{url} returns unexpected data format: {data}")
                continue
            df = pd.DataFrame(data["feed"])
            # sense check data
            if len(df) == 0:
                print(f"URL {url} returns empty data: {df}")
                # log error in error dict
                error_dict[url] = df.to_json()
                continue
            df["time_published"] = pd.to_datetime(df["time_published"])
            print(f"Result has {len(df)} rows from {df['time_published'].min()} to {df['time_published'].max()}")

            # add company and symbol columns
            df["company"] = company
            df["symbol"] = symbol

            df_list.append(df)
        # save to disk for every 10 stocks
        if count % 10 == 0 or count == 503:
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            filename = f"news_part_{int(count / 10)}_{current_datetime}"
            master_df = pd.concat(df_list)
            print(f"Writing {len(master_df)} rows to {filename}")
            master_df.to_csv(filename, index=False, mode="w")
            # reset df_list
            df_list = []

            print(f"Writing error_dict to error_{filename}.json")
            with open(f"error_{filename}.json", "w") as outfile:
                json.dump(error_dict, outfile)
            # reset error_dict
            error_dict = {}


if __name__ == '__main__':
    available = get_available()
    dates = get_dates()
    get_stock_prices(available, dates, skipfirst=100)
