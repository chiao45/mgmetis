# -*- coding: utf-8 -*-
import csv
import numpy as np


def load_mesh():
    f = open("tet.csv")
    reader = csv.reader(f, delimiter=" ")
    _eind = [int(x) for line in reader for x in line]
    _nv = max(_eind) + 1
    _ne = len(_eind) // 4
    return (
        _nv,
        _ne,
        np.asarray(np.arange(0, len(_eind) + 4, 4), dtype="int32"),
        np.asarray(_eind, dtype="int32"),
    )


def load_mesh_uniform():
    nv, _, _, eind = load_mesh()
    return nv, eind.reshape(-1, 4)
