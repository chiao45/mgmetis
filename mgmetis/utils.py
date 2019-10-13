# -*- coding: utf-8 -*-
"""Utility functions

.. module:: mgmetis.utils
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""

import numpy as np

from .enums import ERROR


def get_so(lib):
    """Get the shared object inside `_cython`

    Parameters
    ----------
    lib : {"metis", "metis64", "parmetis", "parmetis64"}
        Library build for METIS

    Returns
    -------
    str
        Abs path to `lib` built inside `/path/to/mgmetis/_cython` with proper
        extensions.

    Raises
    ------
    FileNotFoundError
    """
    import os
    import sysconfig

    so = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "_cython",
        lib + sysconfig.get_config_var("EXT_SUFFIX"),
    )
    if not os.path.isfile(so):
        raise FileNotFoundError(so)
    return so


class MetisInputError(RuntimeError):
    """Exception indicates ``METIS_ERROR_INPUT`` errors
    """


class MetisMemoryError(MemoryError):
    """Exception indicates ``METIS_ERROR_MEMORY`` errors
    """


class MetisError(RuntimeError):
    """Exception indicates ``METIS_ERROR`` errors
    """


METIS_ERRORS = {
    ERROR.INPUT.value: MetisInputError,
    ERROR.MEMORY.value: MetisMemoryError,
    ERROR.ERROR.value: MetisError,
}
"""A exception factory for handling C Metis calls

Examples
--------

>>> ret = 1  # METIS_OK
>>> try:
...     raise METIS_ERRORS[1]("meh")
... except KeyError:
...     pass
"""


def process_mesh(*cells, **kw):
    """Process user input mesh

    For partitioning a mesh for finite element solver, METIS requires the
    input mesh must be stored in compressed storage, analog to a CSR graph.
    This is a general strategy for mixed meshes, but may not be user-friendly
    for typical uniform finite element meshes. `mgmetis` takes either a
    compressed mesh or a uniform mesh and convert them into METIS mesh input.
    In addition, data types are handled as well.

    Parameters
    ----------
    *cells : positional args
        If the input is length 2, then a compressed mesh data structure is
        assumed, i.e., the first entry `cells[0]` contains the cell starting
        position array, while corresponding nodes are stored in `cells[1]`.
        If the input is length 1, then we assume the input is a 2D
        `array_like`, in which each item is a cell stored as a 1D `array_like`,
    nv : int, optional
        Number of vertices in the mesh, if it's negative (default), then the
        routine will compute it on the fly.

    Returns
    -------
    eptr : np.ndarray
        Cell starting position array
    eind : np.ndarray
        Compressed list of node IDs for all cells
    nv : int
        Total number of vertices

    Warnings
    --------

    For efficient using, the caller should supply the total number of vertices
    `nv`, which can be easily known beforehand. Also, for compressed mesh
    input, this routine won't check the consistency between C and Fortran
    index systems. It's the caller's responsibility to ensure the consistency.
    """
    if len(cells) not in (1, 2):
        raise ValueError("input mesh must be either two or a single args")
    if len(cells) == 2:
        eptr, eind = np.asarray(cells[0]).reshape(-1), np.asarray(cells[1]).reshape(-1)
        if not np.issubdtype(eptr.dtype, np.integer):
            # convert to default integer
            eptr = np.asarray(eptr, dtype=int)
        if eptr.dtype != eind.dtype:
            eind = np.asarray(eind, dtype=eptr.dtype)
    else:
        # assume 2D numpy array or list of list
        cells = cells[0]
        try:
            if not np.issubdtype(cells.dtype, np.integer):
                raise AttributeError
            eind = np.asarray(cells.reshape(-1), dtype=cells.dtype)
            # NOTE: assume 2D array
            eptr = np.arange(0, cells.size + 1, cells.shape[1], dtype=cells.dtype)
        except AttributeError:
            eptr = np.cumsum([0] + [len(cell) for cell in cells])
            eind = np.asarray([node for cell in cells for node in cell], dtype=int)
        min_nv = np.min(eind)
        if min_nv not in (0, 1):
            raise ValueError("index must start with 0 or 1")
        if min_nv:
            eptr += 1
    nv = kw.get("nv", -1)
    if nv < 0:
        # NOTE: compute number of vertices
        nv = np.max(eind) + 1 - eptr[0]
    if eptr.dtype.alignment < 4:
        return np.asarray(eptr, dtype=np.int32), np.asarray(eind, dtype=np.int32), nv
    return eptr, eind, nv
