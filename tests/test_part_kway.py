# -*- coding: utf-8 -*-
import numpy as np
import pytest

try:
    from mgmetis.parmetis import part_kway
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    has_mpi = True
except (ImportError, ModuleNotFoundError):
    has_mpi = False


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


def split_graph(rank, dtype=None):
    xadj, adjncy = create_graph(int)
    n = xadj.size // 2
    if rank == 0:
        xadj0 = xadj[: n + 1].copy()
        adjs0 = adjncy[: xadj0[-1]].copy()
        if dtype is None:
            return list(xadj0), (adjs0)
        return np.asarray(xadj0, dtype=dtype), np.asarray(adjs0, dtype=dtype)
    xadj1 = xadj[n:].copy()
    adjs1 = adjncy[xadj1[0] :].copy()
    xadj1 -= xadj1[0]
    if dtype is None:
        return list(xadj1), list(adjs1)
    return np.asarray(xadj1, dtype=dtype), np.asarray(adjs1, dtype=dtype)


@pytest.mark.skipif(not has_mpi or comm.size != 2, reason="invalid parallel env")
def test_partkway():
    try:
        rank = comm.rank
        xadj, adjs = split_graph(rank)
        _, part = part_kway(4, xadj, adjs, comm=comm)
        # NOTE: collect to all processes
        parts = comm.allgather(part)
        part = np.append(parts[0], parts[1])
        assert (
            sum(np.where(part == x)[0].size for x in range(4))
            == len(create_graph()[0]) - 1
        )
    except BaseException as e:
        import sys

        print(e, file=sys.stderr, flush=True)
        comm.Abort(1)


@pytest.mark.skipif(not has_mpi or comm.size != 2, reason="invalid parallel env")
def test_partgeomkway():
    try:
        rank = comm.rank
        xadj, adjs = split_graph(rank)
        _, part = part_kway(
            4, xadj, adjs, comm=comm, xyz=np.random.rand(len(xadj) - 1, 2)
        )
        # NOTE: collect to all processes
        parts = comm.allgather(part)
        part = np.append(parts[0], parts[1])
        assert (
            sum(np.where(part == x)[0].size for x in range(4))
            == len(create_graph()[0]) - 1
        )
    except BaseException as e:
        import sys

        print(e, file=sys.stderr, flush=True)
        comm.Abort(1)
