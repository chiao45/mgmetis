# -*- coding: utf-8 -*-
import numpy as np
from load_mesh import load_mesh, load_mesh_uniform
from mgmetis.metis import part_mesh_dual


def test_c():
    # NOTE: C-based index
    nv, ne, eptr, eind = load_mesh()
    _, epart, npart = part_mesh_dual(4, eptr, eind, nv=nv)  # 4 parts
    assert epart.size == ne
    assert npart.size == nv
    assert sum(np.where(epart == x)[0].size for x in range(4)) == ne

    # NOTE: test without nv input
    _, epart2, npart2 = part_mesh_dual(4, eptr, eind, epart=epart, npart=npart)
    assert epart is epart2
    assert npart is npart2
    assert epart2.size == ne
    assert npart2.size == nv
    assert sum(np.where(epart2 == x)[0].size for x in range(4)) == ne

    # NOTE: test uniform
    _, tets = load_mesh_uniform()
    _, epart3, npart3 = part_mesh_dual(4, tets, epart=epart, npart=npart)
    assert epart is epart3
    assert npart is npart3
    assert epart3.size == ne
    assert npart3.size == nv
    assert sum(np.where(epart3 == x)[0].size for x in range(4)) == ne


def test_c64():
    # NOTE: 64-bit integer
    nv, ne, eptr, eind = load_mesh()
    eptr = np.asarray(eptr, dtype=np.int64)
    eind = np.asarray(eind, dtype=np.int64)
    _, epart, npart = part_mesh_dual(4, eptr, eind, nv=nv)  # 4 parts
    assert epart.size == ne
    assert npart.size == nv
    assert sum(np.where(epart == x)[0].size for x in range(4)) == ne


def test_fortran():
    nv, ne, eptr, eind = load_mesh()
    eptr += 1
    eind += 1

    _, epart, npart = part_mesh_dual(4, eptr, eind, nv=nv)  # 4 parts
    assert epart.size == ne
    assert npart.size == nv
    assert sum(np.where(epart == x + 1)[0].size for x in range(4)) == ne
