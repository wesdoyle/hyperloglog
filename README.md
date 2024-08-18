# HyperLogLog exploration 

This repo explores implementations of the [HyperLogLog](https://www.wikipedia.org/wiki/HyperLogLog) algorithm for estimating the cardinality of a dataset.

These are basic implementations for learning purposes.

## Example using text file on disk

```sh
> python3 ./py-version/hyperloglog.py ./data/complete_works_of_shakespeare.txt 16
Comparison of HyperLogLog vs Exact Counting
----------------------------------------------------------
Method         Count     Error (%)
----------------------------------------------------------
HyperLogLog    25838     0.37
Exact          25934     N/A
----------------------------------------------------------
```

## Example using sqlite database on disk

This example uses the [Wikibooks dataset](https://www.kaggle.com/datasets/dhruvildave/wikibooks-dataset) (license is [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/))

```sh
> python3 ./py-version/hll_sqlite.py ./data/wikibooks.sqlite en body_text 20

```
