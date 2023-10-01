# dissertation
Comparison of Lexicon-Based and Model-Based Sentiment Analysis Techniques to Predict Stock Market

## Set up

To update conda env, run

```bash
conda env update --file env.yml --prune
```

To add kernel to Jupyter, run
```bash
conda activate dissertation
python -m ipykernel install --user --name dissertation
```
## Structure
Given that Engage has a limit of 20 files, I have uploaded only the core sections into Engage.
The full code base is available at https://github.com/waijean-msc/dissertation.

Note that certain data files are too large (exceeded the maximum file size of 50MB in Engage) 
hence they are not uploaded. Please reach out to me if you require the original data files.

- analysis: 
  - combine_pred: combine the prediction of lexicon and model-based methods into a single file
  - holding_period: create multiple holding periods
  - analysis.ipynb: create classification labels and evaluate performance
- lexicon: implementation of lexicon-based methods
- model: implementation of model-based methods
- news: collection of financial news articles
  - news_v1: New York Times API
  - news_v2: Alpha Vantage API
- stock_price: collection of stock price data


