import pandas as pd
import json


def str_to_dict(s):
    s = s.replace("\'", "\"")
    d = json.loads(s)
    return d


def parse_result(series):
    dict_0, dict_1, dict_2 = [str_to_dict(s) for s in (series[0], series[1], series[2])]
    master_dict = {d["label"]: d["score"] for d in (dict_0, dict_1, dict_2)}

    return pd.Series(master_dict)


if __name__ == '__main__':
    df = pd.read_csv("../../news/news_v2/analysis/news_v2.1.csv")

    lexicon_df = pd.read_csv("../../lexicon/lexicon_v2.csv")

    finbertv1_df = pd.read_csv("../../model/second_run/finbertv1.csv")
    finbertv2_df = pd.read_csv("../../model/second_run/finbertv2.csv")

    finbertv1_processed_df = finbertv1_df.apply(parse_result, axis=1)
    finbertv2_processed_df = finbertv2_df.apply(parse_result, axis=1)

    lexicon_df.columns = ["lexicon_" + col for col in lexicon_df.columns]
    finbertv1_processed_df.columns = ["finbertv1_" + col for col in finbertv1_processed_df.columns]
    finbertv2_processed_df.columns = ["finbertv2_" + col for col in finbertv2_processed_df.columns]

    combined_df = pd.concat([df, lexicon_df, finbertv1_processed_df, finbertv2_processed_df], axis=1)

    combined_df.to_csv("news_v2.1_pred.csv", index=False)
