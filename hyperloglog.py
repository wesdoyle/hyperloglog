"""
HyperLogLog is used to estimate the number of 
distinct elements in a large data set with a 
relatively small memory footprint. 

Links:
- https://chengweihu.com/hyperloglog/
- https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
- https://en.wikipedia.org/wiki/HyperLogLog

"""

import sys


class HyperLogLog:

    # -- Notes --
    # let "hash(D)" hash data from domain D to the binary domain
    # let p(s) for s in the binary domain be the position of the leftmost 1-b (p(0001...) === 4)
    # The algorithm hll(M) where M is a multiset of items from a domain of hashed data:
    # M[m] is a collection of registers of length m, M[1], ..., M[m] -> -inf;
    # for v in M:
    #   x := hash(v) 
    #   j := 1 + <x_1,x_2,..x_b>_2 (the binary addr determined by the first b bits of x)
    #   w := x_b+1, x_b+2, ...
    #   M[j] := max(M[j], p(w))
    #   Z := 1/(sum from j=1 to m) of (2^-M[j])) "the indicator function"
    #   return  E:= alpha_m * m^2 * Z with alpha_m given by the eqn for harmonic mean

    def __init__(self):
        pass

    def add(self):
        pass

    def count(self):
        pass

    def _hash(self, v):
        h = hash(v)

    def _rho(self):
        pass


def process_file(file_path):
    hll = HyperLogLog()
    with open(file_path, 'r', encoding='utf-8') as f:
        result = hll.process(f)
        return result

def main():
    file_path = './test.txt'
    result = process_file(file_path)