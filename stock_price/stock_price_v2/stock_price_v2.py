import pandas as pd
import time
import datetime
import json


def get_available():
    url = "https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=demo"
    stock_df = pd.read_csv(url)
    available = set(stock_df["symbol"])
    return available


def get_stock_prices(available, skipfirst: int):
    sp500_df = pd.read_csv("sp500.csv")
    api_key = "8VUOFOJS4BENDZG9"

    df_list = []  # to store stock price
    error_dict = {}  # to store error URL

    for index, symbol in sp500_df["Symbol_modified"].iteritems():
        count = index + 1
        if count <= skipfirst:
            continue
        print(f"Processing {count}-th symbol: {symbol}")
        if symbol not in available:
            print(f"The following symbol is not available: {symbol}")
            # log error in error dict
            error_dict[symbol] = "Not available"
            continue
        for year in [1, 2]:
            for month in range(1, 13):
                url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED"
                # format url
                url += f"&symbol={symbol}"
                url += "&interval=5min"  # 1min, 5min, 15min, 30min, 60min
                url += f"&slice=year{year}month{month}"
                url += f"&apikey={api_key}"
                print(url)

                # retry for 10 times in case server is unavailable
                for i in range(0, 10):
                    try:
                        df = pd.read_csv(url)
                        # 30 requests per minute so sleep 2 seconds between requests
                        time.sleep(2)
                    except Exception as e:
                        print(e)
                        if i == 9:
                            raise
                        else:
                            continue
                    break
                # sense check data
                if len(df) < 5:
                    print(f"URL {url} returns incorrect data: {df}")
                    # log error in error dict
                    error_dict[url] = df.to_json()
                    continue
                df["time"] = pd.to_datetime(df["time"])
                print(f"Result has {len(df)} rows from {df['time'].min()} to {df['time'].max()}")
                df["symbol"] = symbol
                df_list.append(df)
        # save to disk for every 10 stocks
        if count % 10 == 0 or count == 503:
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            filename = f"stock_price_part_{int(count / 10)}_{current_datetime}"
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
    get_stock_prices(available, skipfirst=500)
