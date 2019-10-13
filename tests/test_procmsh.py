# -*- coding: utf-8 -*-
import numpy as np
from mgmetis.utils import process_mesh


def test_procmsh():
    eptr, eind, nv = process_mesh([0, 3, 6], [0, 1, 2, 1, 3, 2])
    assert eptr.dtype == int
    assert list(eind) == [0, 1, 2, 1, 3, 2]
    assert nv == 4

    # 1-based index
    eptr, eind, nv = process_mesh([[1, 2, 3], [2, 4, 3]])
    assert list(eptr) == [1, 4, 7]
    assert nv == 4
    assert list(eind) == [1, 2, 3, 2, 4, 3]

    eptr, eind, nv = process_mesh([[0, 1, 2], [3, 4, 5, 6, 7], [3]])
    assert nv == 8
    assert list(eptr) == [0, 3, 8, 9]
    assert list(eind) == [0, 1, 2, 3, 4, 5, 6, 7, 3]


def test_procmsh_np():
    eptr, eind, nv = process_mesh(
        np.asarray([0, 3, 6], dtype=np.int32),
        np.asarray([0, 1, 2, 1, 3, 2], dtype=np.int32),
    )
    assert eptr.dtype == np.int32
    assert list(eind) == [0, 1, 2, 1, 3, 2]
    assert nv == 4

    # 1-based index
    eptr, eind, nv = process_mesh(np.asarray([[1, 2, 3], [2, 4, 3]], dtype=np.int32))
    assert list(eptr) == [1, 4, 7]
    assert nv == 4
    assert list(eind) == [1, 2, 3, 2, 4, 3]
