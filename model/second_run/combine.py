import pandas as pd

if __name__ == '__main__':
    # combine v1
    df1 = pd.read_csv("finbert_v1_part1_7900.csv")
    df2 = pd.read_csv("finbert_v1_part2_30000.csv")
    df3 = pd.read_csv("finbert_v1_part3_29700.csv")
    df4 = pd.read_csv("finbert_v1_part4_9400.csv")
    df5 = pd.read_csv("finbert_v1_part5_11167.csv")

    all_v1_df = pd.concat([df1, df2, df3, df4, df5])
    assert len(all_v1_df) == 88167
    all_v1_df.to_csv("finbert_v1.csv", index=False)

    # combine v2
    df1 = pd.read_csv("finbert_v2_part1_14100.csv")
    df2 = pd.read_csv("finbert_v2_part2_29800.csv")
    df3 = pd.read_csv("finbert_v2_part3_28600.csv")
    df4 = pd.read_csv("finbert_v2_part4_15667.csv")

    all_v2_df = pd.concat([df1, df2, df3, df4])
    assert len(all_v2_df) == 88167
    all_v2_df.to_csv("finbert_v2.csv", index=False)
