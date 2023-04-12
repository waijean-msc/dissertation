import pandas as pd
import time
import requests


def query(url, sentences):
    payload = {
        "inputs": sentences,
        "options": {"wait_for_model": True}
    }

    API_TOKEN = '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'
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    response = requests.post(url, headers=headers, json=payload)

    return response.json()


def split(list_a, chunk_size):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]


if __name__ == '__main__':
    # API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
    API_URL = "https://api-inference.huggingface.co/models/yiyanghkust/finbert-tone"
    model_name = "finbert_v2"

    df = pd.read_csv("../news_stock_price.csv")
    df["summary_title"] = df["summary"].combine_first(df["title"])

    # convert to list
    summary_title_list = df["summary_title"].to_list()
    # check all string instances
    all([isinstance(sent, str) for sent in summary_title_list])

    # chunk into smaller size
    chunk_size = 100
    chunk_summary_title_list = list(split(summary_title_list, chunk_size))
    # check chunked list is equivalent to original list
    assert len(summary_title_list) == sum([len(l) for l in chunk_summary_title_list])

    p_list = []
    for i, l in enumerate(chunk_summary_title_list):
        # skip the first n if it has been processed
        if i < 1418:
            continue
        print(f"Processing {i}/{len(chunk_summary_title_list)}")
        print(f"Number of sentences per chunk list: {len(l)}")
        # truncate maximum number of characters for the model (512)
        max_char = 512
        truncated_l = [sent[:max_char] if len(sent) > max_char else sent for sent in l]
        try:
            p = query(url=API_URL, sentences=truncated_l)
        except:
            print("Error with API")

        if len(p) == len(l):
            p_list.extend(p)
        else:
            print(f"API returns unexpected length: {len(p)}: {p}")

    # df = pd.DataFrame(p_list)
    # df.to_csv(f"{len(p_list)}_{model_name}_part2.csv", index=False)

    df[f"{model_name}_result"] = p_list
    df.to_csv(f"{model_name}_pred.csv", index=False)