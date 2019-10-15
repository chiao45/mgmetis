# -*- coding: utf-8 -*-
"""Demo program of using Kway algorithm for the graph in doc
"""

cimport mgmetis.metis as metis  # 32 bit

import numpy as np


xadj = np.asarray(
    [int(x) for x in "0 2 5 8 11 13 16 20 24 28 31 33 36 39 42 44".split()],
    dtype=np.int32,
)
cdef metis.idx_t nv = xadj.size - 1
cdef metis.idx_t[:] xadj_view = xadj

adjs = np.asarray(
    [
        int(x)
        for x in "1 5 0 2 6 1 3 7 2 4 8 3 9 0 6 10 1 5 7 11 2 6 8 12 3 7 9 13 4 8 14 5 11 6 10 12 7 11 13 8 12 14 9 13".split()
    ],
    dtype=np.int32
)
cdef metis.idx_t[:] adjs_view = adjs

cdef metis.idx_t ncon = 1
cdef metis.idx_t nparts = 4  # four parts

# outputs
cdef metis.idx_t edgecut
part = np.empty(nv, dtype=np.int32)
cdef metis.idx_t[:] part_view = part

# call metis
cdef int ret = metis.PartGraphKway(
    &nv,
    &ncon,
    &xadj_view[0],
    &adjs_view[0],
    NULL,
    NULL,
    NULL,
    &nparts,
    NULL,
    NULL,
    NULL,
    &edgecut,
    &part_view[0]
)
if ret != metis.OK:
    raise ValueError


print("edgecut=", edgecut)
print("part=", part)
