# -*- coding: utf-8 -*-
import numpy as np
import pytest

try:
    from load_mesh import load_mesh
    from mgmetis.parmetis import part_mesh_kway
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    has_mpi = True
except (ImportError, ModuleNotFoundError):
    has_mpi = False


@pytest.mark.skipif(not has_mpi or comm.size != 2, reason="invalid parallel env")
def test_partmeshkway():
    try:
        _, ne, _, eind = load_mesh()
        nes = [ne // 2, ne - ne // 2]
        my_ne = nes[comm.rank]
        if comm.rank == 0:
            my_eind = eind[: 4 * my_ne].copy()
        else:
            my_eind = eind[4 * nes[0] :].copy()
        eptr = np.arange(0, len(my_eind) + 1, 4, dtype=eind.dtype)
        _, part = part_mesh_kway(4, eptr, my_eind)
        # NOTE: collect to all processes
        parts = comm.allgather(part)
        part = np.append(parts[0], parts[1])
        assert sum(np.where(part == x)[0].size for x in range(4)) == ne
    except BaseException as e:
        import sys

        print(e, file=sys.stderr, flush=True)
        comm.Abort(1)
