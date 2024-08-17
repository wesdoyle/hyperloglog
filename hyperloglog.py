"""
HyperLogLog is used to estimate the number of 
distinct elements in a large data set with a 
relatively small memory footprint. 

Links:
- https://chengweihu.com/hyperloglog/
- https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/
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

    # From Wikipedia: 
    # > The HyperLogLog has three main operations: 
    # > add to add a new element to the set, 
    # > count to obtain the cardinality of the set and 
    # > merge to obtain the union of two sets. 


    def __init__(self):
        self.precision = 8 
        self.m = 1 << precision # i.e. [1 0 0 0 0 0 0 0 0]
        self.registers = [0] * self.m

    def add(self, v):
        """
        Add a new element to the estimator.
        This hashes the input value and gets two parts of the hash: j and w.
        j is used to select register, and w contains the remaining bits of the hash. 
        w is used to potentially update the value at that register.
        The register is updated with whichever is larger, its current value or the result of _rho(w).

        _rho just calculates the position of the _leftmost_ 1-bit in the binary representation of w.
        in other words, it is the count of leading zeroes + 1

        we're keeping track of the rarest event we've seen for each register.
        a long run of leading zeroes is a rare event - longer runs are more rare.
        by keeping the maximum _rho(w) for each register, 
        we're essentially recording the rarest event we've 
        seen for that portion of the hash space.

        a precision parameter can be used to choose a number of registers.
        the larger the number of buckets, the greater precision, because we'll
        be able to capture more unique events.

        :param v: the value to be added to the estimator
        """
        x = self._hash(v)
        j = x & (self.m-1) # efficient modulo
        """
        Why subtract 1 from m before ANDing?
        m   = 8 = 1000
        m-1 = 7 = 0111

        By subtracting 1, we create a bit mask that captures the least significant bits:
        1000 - 1 = 0111

        This mask, when used with AND, effectively performs the modulo operation, selecting a register:
        Any number AND 0111 will result in a value between 0 and 7,
        which is equivalent to that number modulo 8.
        """
        w = x >> self.precision
        self.registers[j] = max(self.registers[j], self._rho(w))

    def count(self):
        pass

    def _hash(self, v):
        return hash(v) & self.mask

    def _rho(self, w):
        """
        This is a ranking function or "leading zero count" (LZC) function
        The intuition behind rho(w):
        In a uniform random binary number, the probability of seeing a run of n leading zeros is 2^(-n).
        By keeping track of the maximum number of leading zeros we've seen for each register, we're essentially tracking the "rarest" event for that register.
        These "rarest events" across all registers can be used to estimate the number of unique elements we've seen.

        :param w:
        """
        return 32 - (w & 31).bit_length() if w else 32


def process_file(file_path):
    hll = HyperLogLog()
    with open(file_path, 'r', encoding='utf-8') as f:
        result = hll.process(f)
        return result

def main():
    file_path = './test.txt'
    result = process_file(file_path)