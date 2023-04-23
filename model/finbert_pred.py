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

    return response


def split(list_a, chunk_size):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]


if __name__ == '__main__':
    # API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
    API_URL = "https://api-inference.huggingface.co/models/yiyanghkust/finbert-tone"
    model_name = "finbert_v2"

    df = pd.read_csv("../news/news_v2/analysis/news_v2.1.csv")

    # convert to list
    summary_title_list = df["model_input"].to_list()
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
        if i < 725:
            continue
        print(f"Processing {i}/{len(chunk_summary_title_list)}")
        print(f"Number of sentences per chunk list: {len(l)}")
        # truncate maximum number of characters for the model (512)
        max_char = 512
        truncated_l = [sent[:max_char] if len(sent) > max_char else sent for sent in l]

        # retry for 10 times in case server is unavailable
        for retry in range(0, 10):
            try:
                response = query(url=API_URL, sentences=truncated_l)
                p = response.json()
            except Exception as e:
                print(e)
                if retry == 9:
                    raise
                else:
                    continue
            else:
                if len(p) == len(l):
                    break
                elif 'error' in p:
                    if 'Rate limit reached.' in p["error"]:
                        raise Exception
                else:
                    print(f"API returns unexpected length: {len(p)}: {p}")
                    if retry == 9:
                        raise Exception
                    else:
                        continue

        p_list.extend(p)

    # df = pd.DataFrame(p_list)
    # df.to_csv(f"{model_name}_part3_{len(p_list)}.csv", index=False)

    df[f"{model_name}_result"] = p_list
    df.to_csv(f"{model_name}_pred.csv", index=False)
