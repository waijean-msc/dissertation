import pandas as pd

# unit is 5-minute
FORWARD_FILL_LIMIT = 5
RETURN_WINDOW = 5


def fill_missing_minutes(df, limit=FORWARD_FILL_LIMIT):
    """
    Forward fill missing minutes with a maximum limit of `limit`.
    """
    date = df["date"].iloc[0]
    index = pd.date_range(start=f'{date} 04:00:00', end=f'{date} 20:00:00', freq='5T')
    metrics_col = ["open", "high", "low", "close", "volume"]
    # forward fill maximum of FORWARD_FILL_LIMIT
    filled_df = df.set_index("datetime").sort_index()[metrics_col].reindex(index, method="ffill", limit=limit)
    filled_df.index.name = "datetime"
    return filled_df


def calculate_return(df, window=RETURN_WINDOW):
    """
    Calculate percentage return in the next `window` 5-minute interval.
    """
    df = df.copy()
    df["datetime_next"] = df["datetime"] + pd.Timedelta(minutes=5 * window)
    merged_df = df.merge(df[["symbol", "datetime", "close"]],
                         left_on=["symbol", "datetime_next"],
                         right_on=["symbol", "datetime"],
                         suffixes=("_before", "_after")
                         ).drop(columns="datetime_next")
    merged_df["pct_return"] = merged_df["close_after"] / merged_df["close_before"] - 1
    return merged_df


def get_stock_return_df():
    stock_df = pd.read_csv("../../stock_price/stock_price_v2/stock_price_v2.csv",
                           parse_dates=["time"])
    stock_df.rename(columns={"time": "datetime"}, inplace=True)
    stock_df.drop_duplicates(inplace=True)

    # check no duplicate datetime per symbol
    assert stock_df.groupby("symbol").apply(lambda x: x["datetime"].duplicated().any()).any() == False

    # create date and time columns
    stock_df["date"] = stock_df["datetime"].dt.normalize()
    stock_df["time"] = stock_df["datetime"].dt.time

    print(stock_df.info())

    filled_stock_df = stock_df.groupby(["symbol", "date"]).apply(fill_missing_minutes).reset_index().dropna()

    print(f"Before forward fill: {len(stock_df):,}")
    print(f"After forward fill: {len(filled_stock_df):,}")

    filled_stock_return_df = calculate_return(filled_stock_df).dropna()

    assert (
            filled_stock_return_df["datetime_after"] - filled_stock_return_df["datetime_before"]
            ==
            pd.Timedelta(minutes=5 * RETURN_WINDOW)
    ).all()

    return filled_stock_return_df


def get_news_df():
    news_df = pd.read_csv("../news.csv", parse_dates=["time_published"])

    print(news_df.info())

    # round up to 5-minute level
    news_df["time_published_5min"] = news_df["time_published"].dt.floor(freq="5T")

    return news_df


if __name__ == '__main__':
    stock_return_df = get_stock_return_df()

    news_df = get_news_df()

    news_price_df = news_df.merge(stock_return_df,
                                  how="left",
                                  left_on=["symbol", "time_published_5min"],
                                  right_on=["symbol", "datetime_before"],
                                  validate="many_to_one")

    filtered_news_price_df = news_price_df.dropna(subset=["pct_return"])
    filtered_pct = len(filtered_news_price_df) / len(news_price_df)
    print(f"Filter percentage {filtered_pct:.2%}")
    print(f"Sample size before filtering: {len(news_df):,}")
    print(f"Sample size after filtering: {len(filtered_news_price_df):,}")

    print(filtered_news_price_df.info())

    filtered_news_price_df.to_csv("news_stock_price_v2.csv", index=False)
