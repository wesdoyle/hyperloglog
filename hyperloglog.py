"""
HyperLogLog is used to estimate the number of distinct elements in a large data set
with a relatively small memory footprint. 
- https://questdb.io/glossary/hyperloglog/
- https://en.wikipedia.org/wiki/HyperLogLog
"""

import sys


class HyperLogLog:
    def __init__(self):
        pass

    def add(self):
        pass

    def _hash(self, v):
        h = hash(v)

    def _rho(self):
        pass

    def count(self):
        pass

def process_file(file_path):
    hll = HyperLogLog()
    with open(file_path, 'r', encoding='utf-8') as f:
        result = hll.process(f)
        return result

def main():
    file_path = './test.txt'
    result = process_file(file_path)