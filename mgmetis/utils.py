# -*- coding: utf-8 -*-
"""Utility functions

.. module:: mgmetis.utils
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""

import ctypes as c

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


_METIS_ERRORS = {
    ERROR.INPUT.value: MetisInputError,
    ERROR.MEMORY.value: MetisMemoryError,
    ERROR.ERROR.value: MetisError,
}
"""A exception factory for handling C Metis calls

Examples
--------

>>> ret = 1  # METIS_OK
>>> try:
...     raise _METIS_ERRORS[1]("meh")
... except KeyError:
...     pass
"""


def _handle_metis_ret(ret, func, args):
    # helper for handling metis function return
    try:
        raise _METIS_ERRORS[ret]("{}:{}:{}".format(func.__name__, ret, args))
    except KeyError:
        # NOTE: METIS_OK
        pass


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
    total_len = eptr[-1] - eptr[0]
    if total_len < eind.size:
        raise ValueError("fatal mesh eind length issue")
    if total_len > eind.size:
        import warnings  # pylint: disable=import-outside-toplevel

        warnings.warn("eind has more entries than eptr[-1]-eptr[0]")
    nv = kw.get("nv", -1)
    if nv < 0:
        # NOTE: compute number of vertices
        nv = np.max(eind) + 1 - eptr[0]
    if eptr.dtype.alignment < 4:
        return np.asarray(eptr, dtype=np.int32), np.asarray(eind, dtype=np.int32), nv
    return eptr, eind, nv


def process_graph(xadj, adjncy):
    """Process user input graph to ensure numpy arrays

    Parameters
    ----------
    xadj : array_like
        1D list of starting positions of the graph nodes
    adjncy : array_like
        1D list of adjacent node list, splitted by `xadj` for each node

    Returns
    -------
    xadj : np.ndarray
        Numpy array of `xadj`
    adjncy : np.ndarray
        Numpy array of `adjncy`
    nv : int
        Number of vertices

    See Also
    --------
    process_mesh
    """
    xadj = np.asarray(xadj).reshape(-1)
    if not np.issubdtype(xadj.dtype, np.integer):
        xadj = np.asarray(xadj, dtype=int)
    if xadj[0] not in (0, 1):
        raise ValueError("the first value of xadj must be 0 (C) or 1 (Fortran)")
    adjncy = np.asarray(adjncy, dtype=xadj.dtype).reshape(-1)
    total_len = xadj[-1] - xadj[0]
    if total_len < adjncy.size:
        raise ValueError("fatal mesh adjncy length issue")
    if total_len > adjncy.size:
        import warnings  # pylint: disable=import-outside-toplevel

        warnings.warn("adjncy has more entries than xadj[-1]-xadj[0]")
    return xadj, adjncy, xadj.size - 1


def as_pointer(ar):
    """Helper function to get the array starting memory address

    This function simply wraps around of `np.ndarray.ctypes.data_as`. In
    addition, if `ar` is None, then None will be returned indicating ``NULL``
    pointer.

    Parameters
    ----------
    ar : {np.ndarray, None}
        Either a valid array or a ``NULL`` pointer

    Returns
    -------
    ctypes.POINTER or None
        The starting memory address of the given array or ``NULL``.

    Warnings
    --------

    The caller needs to ensure `ar` won't be GL-ed while interfacing with the
    low level memory addresses.
    """

    if ar is None:
        return None
    return ar.ctypes.data_as(c.POINTER(np.ctypeslib.as_ctypes_type(ar.dtype)))


def get_or_create_workspace(kw, key, n, dtype):
    """Get the the buffer from user key-worded inputs or create one

    Parameters
    ----------
    kw : dict
        Implicitly converted from key-worded inputs
    key : str
        Key in `kw`
    n : int
        Size of the array
    dtype : np.dtype
        Data type for the output array

    Returns
    -------
    np.ndarray
        If `key` value exists in `kw` and it's an array of data type `dtype`,
        then it will be wrapped. Otherwise, a new array will be created and
        returned.
    """
    # helper to create or get the user workspace
    v = kw.get(key, None)
    v = np.asarray(v if v is not None else np.empty(n, dtype=dtype), dtype=dtype)
    if v.size < n:
        raise ValueError("{} should be at least size of {}".format(key, n))
    return v


def try_get_input_array(kw, key, n, dtype):
    """Try to get an input argument from user key-worded inputs

    Parameters
    ----------
    kw : dict
        Implicitly converted from key-worded inputs
    key : str
        Key in `kw`
    n : int
        Size of the input array
    dtype : np.dtype
        Data type of the array

    Returns
    -------
    {np.ndarray, None}
        Return None if ``key is not in kw``.
    """
    v = kw.get(key, None)
    if v is None:
        return None
    v = np.asarray(v, dtype=dtype)
    if v.size < n:
        raise ValueError("{} should b e at least size of {}".format(key, n))
    return v
