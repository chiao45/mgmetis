# -*- coding: utf-8 -*-
import numpy as np
import pytest

try:
    from mgmetis.parmetis import part_geom
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    has_mpi = True
except (ImportError, ModuleNotFoundError):
    has_mpi = False


@pytest.mark.skipif(not has_mpi or comm.size != 2, reason="invalid parallel env")
def test_partgeom():
    try:
        part = part_geom(np.random.rand(100, 3))
        assert np.max(np.asarray(comm.allgather(part))) == 1
    except BaseException as e:
        import sys

        print(e, file=sys.stderr, flush=True)
        comm.Abort(1)
