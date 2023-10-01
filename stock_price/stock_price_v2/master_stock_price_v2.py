import json
from os import listdir
import pandas as pd


def load_data(date_file_dir, data_files):
    df_list = []
    for file_name in data_files:
        print(f"Reading file: {file_name}")
        df = pd.read_csv(date_file_dir + file_name)
        df_list.append(df)

    master_df = pd.concat(df_list)

    master_df.to_csv("stock_price_v2.csv", index=False)


def load_error(date_file_dir, error_files):
    master_dict = {}
    for file_name in error_files:
        print(f"Reading file: {file_name}")
        with open(date_file_dir + file_name, 'r') as file:
            data = file.read()
        data = json.loads(data)
        master_dict.update(data)

    return master_dict


if __name__ == '__main__':
    date_file_dir = "data/"
    files = listdir(date_file_dir)

    error_files = [f for f in files if 'error' in f]
    data_files = [f for f in files if 'error' not in f]

    # load_data(date_file_dir, data_files)

    error_dict = load_error(date_file_dir, error_files)

    print(error_dict)
