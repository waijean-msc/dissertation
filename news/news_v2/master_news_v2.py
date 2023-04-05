from os import listdir
import pandas as pd

if __name__ == '__main__':
    date_file_dir = "./second_run/"

    files = listdir(date_file_dir)

    data_files = [f for f in files if 'error' not in f]

    df_list = []
    for file_name in data_files:
        df = pd.read_csv(date_file_dir + file_name)
        df_list.append(df)

    master_df = pd.concat(df_list)

    master_df.to_csv("news_v2.csv", index=False)
