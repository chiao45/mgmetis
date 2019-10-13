# -*- coding: utf-8 -*-
import numpy as np
from mgmetis.metis import part_graph_kway


def create_graph(dtype=None):
    # NOTE: test the example in the documentation
    xadj = [int(x) for x in "0 2 5 8 11 13 16 20 24 28 31 33 36 39 42 44".split()]
    adjncy = [
        int(x)
        for x in "1 5 0 2 6 1 3 7 2 4 8 3 9 0 6 10 1 5 7 11 2 6 8 12 3 7 9 13 4 8 14 5 11 6 10 12 7 11 13 8 12 14 9 13".split()
    ]
    if dtype is None:
        return xadj, adjncy
    return np.asarray(xadj, dtype=dtype), np.asarray(adjncy, dtype=dtype)


def test_c():
    _, part = part_graph_kway(4, *create_graph("int32"))
    assert (
        sum(np.where(part == x)[0].size for x in range(4)) == len(create_graph()[0]) - 1
    )


def test_c64():
    # NOTE: implicit test converting from list to np.ndarray as well
    _, part = part_graph_kway(4, *create_graph())
    assert (
        sum(np.where(part == x)[0].size for x in range(4)) == len(create_graph()[0]) - 1
    )


def test_fortran():
    xadj, adjs = create_graph("int32")
    xadj += 1
    adjs += 1
    _, part = part_graph_kway(4, xadj, adjs)
    assert sum(np.where(part == x + 1)[0].size for x in range(4)) == xadj.size - 1
