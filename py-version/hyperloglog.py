"""
HyperLogLog is used to estimate the number of 
distinct elements in a large data set with a 
relatively small memory footprint. 

Links:
- https://static.googleusercontent.com/media/research.google.com/en/us/pubs/archive/40671.pdf
- https://engineering.fb.com/2018/12/13/data-infrastructure/hyperloglog/
- https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/
- https://en.wikipedia.org/wiki/HyperLogLog
- https://chengweihu.com/hyperloglog/
- https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
"""

import sys
import math
import re
import mmh3
import hashlib
import numpy as np

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

# From Wikipedia: 
# > The HyperLogLog has three main operations: 
# > add to add a new element to the set, 
# > count to obtain the cardinality of the set and 
# > merge to obtain the union of two sets. 

class HyperLogLog:
    def __init__(self, precision=14):
        self.p = precision
        self.m = 1 << self.p  # 2^p
        self.registers = [0] * self.m 
        self.alpha_m = self._get_alpha()

    def _get_alpha(self):
        # See Fig.3 from original paper:
        # - https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf
        if self.m <= 16:
            return 0.673
        if self.m <= 32:
            return 0.697
        if self.m <= 64:
            return 0.709
        return 0.7213 / (1 + 1.079 / self.m)


    def _hash(self, value: str) -> int:
        # hashed_result = mmh3.hash(str(value), seed=77) & 0xFFFFFFFF
        hashed_result = int(hashlib.md5(value.encode('utf8')).hexdigest(), 16)
        return hashed_result


    def _rho(self, w: int) -> int:
        if w == 0:
            return 32 - self.p
        # Get the position of the leftmost 1-bit (counting from the most significant bit)
        return (w.bit_length() - 1).bit_length()


    def add(self, v):
        hashed_value = self._hash(v)
        j = hashed_value & (self.m - 1)
        w = (hashed_value >> self.p) & 0xFFFFFFFF
        self.registers[j] = max(self.registers[j], self._rho(w))


    def count(self):
        # Calculate the harmonic mean
        Z = 1 / sum([2.0 ** -b for b in self.registers])
        E = self.alpha_m * self.m ** 2 * Z 

        # Apply bias correction
        if E <= 2.5 * self.m:
            V = self.registers.count(0)
            if V > 0:
                E = self.m * math.log(self.m / V)
        elif E > 1 / 30.0:
            E = -(2 ** 128) * math.log(1 - E / (2 ** 128))

        result = int(E)
        return result


def process_file_hll(file_path: str, precision: int) -> int:
    hll = HyperLogLog(precision=precision)

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            tokens = re.findall(r'\w+', line.lower())  # Use regex to match words
            for token in tokens:
                hll.add(token)
    result = hll.count()
    return result 


def process_file_exact(file_path):
    unique_tokens = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            tokens = re.findall(r'\w+', line.lower())
            unique_tokens.update(tokens)
    return len(unique_tokens)


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <file_path> <precision>")
        sys.exit(1)

    file_path = sys.argv[1]
    precision = int(sys.argv[2])

    # HyperLogLog estimation
    hll_result = process_file_hll(file_path, precision)

    # Exact counting
    exact_result = process_file_exact(file_path)
    error_percentage = abs(hll_result - exact_result) / exact_result * 100

    print("\nComparison of HyperLogLog vs Exact Counting")
    print("-" * 58)
    print(f"{'Method':<15}{'Count':<10}{'Error (%)':<10}")
    print("-" * 58)
    print(f"{'HyperLogLog':<15}{hll_result:<10d}{error_percentage:<10.2f}")
    print(f"{'Exact':<15}{exact_result:<10d}{'N/A':<10}")
    print("-" * 58)


if __name__ == '__main__':
    main()