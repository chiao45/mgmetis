# -*- coding: utf-8 -*-
"""Parallel interface of METIS, ParMETIS

.. module:: mgmetis.parmetis
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""

import ctypes as c

import numpy as np

from .par_utils import get_comm, determine_wgtflag, build_proc_dist, is_par, comm_ptr
from .utils import (
    get_so,
    _handle_metis_ret,
    get_or_create_workspace,
    try_get_input_array,
    as_pointer,
    process_graph,
    process_mesh,
)


class _LibParMetisModule:
    _IDX_T = c.c_int32

    def __new__(cls, lib):
        try:
            so = get_so(lib)
        except FileNotFoundError:
            raise ModuleNotFoundError(
                "ParMETIS is not available, please install mpi4py and rebuild mgmetis"
            )
        else:
            so_obj = c.CDLL(so)
            instance = super().__new__(cls)
            try:
                instance.__setup(so_obj)
            finally:
                del so_obj
            return instance

    @classmethod
    def __setup(cls, so_obj):
        # PartKway
        cls.__set_parmetis_func(
            so_obj, "PartKway", ["i*"] * 9 + ["f*"] * 2 + ["i*"] * 3
        )
        # PartGeomKway
        cls.__set_parmetis_func(
            so_obj,
            "PartGeomKway",
            ["i*"] * 8 + ["f*"] + ["i*"] * 2 + ["f*"] * 2 + ["i*"] * 3,
        )
        # PartGeom
        cls.__set_parmetis_func(so_obj, "PartGeom", ["i*"] * 2 + ["f*", "i*"])
        # RefineKway
        cls.__set_parmetis_func(
            so_obj, "RefineKway", ["i*"] * 9 + ["f*"] * 2 + ["i*"] * 3
        )
        # AdaptiveRepart
        cls.__set_parmetis_func(
            so_obj, "AdaptiveRepart", ["i*"] * 10 + ["f*"] * 3 + ["i*"] * 3
        )
        # Mesh2Dual
        cls.__set_parmetis_func(so_obj, "Mesh2Dual", ["i*"] * 5 + ["i**"] * 2)
        # PartMeshKway
        cls.__set_parmetis_func(
            so_obj, "PartMeshKway", ["i*"] * 9 + ["f*"] * 2 + ["i*"] * 3
        )
        # NodeND
        cls.__set_parmetis_func(so_obj, "NodeND", ["i*"] * 7)
        # V32_NodeND
        cls.__set_parmetis_func(so_obj, "V32_NodeND", ["i*"] * 9 + ["f*"] + ["i*"] * 4)
        # SerialNodeND NOTE: last one
        _all = cls.__set_parmetis_func(so_obj, "SerialNodeND", ["i*"] * 7)
        # NOTE: add __all__ to support `from mgmetis.parmetis.libparmetis import *`
        setattr(cls, "__all__", _all)

    @classmethod
    def __set_parmetis_func(
        cls, so_obj, fname, args, _all=[]
    ):  # pylint: disable=dangerous-default-value
        try:
            c_func = so_obj["ParMETIS_V3_{}".format(fname)]
        except BaseException:
            c_func = so_obj["ParMETIS_{}".format(fname)]
        c_func.restype = c.c_int  # integer return
        c_args = []
        for arg in args:
            t = cls._IDX_T if arg.startswith("i") else c.c_float
            # We treat MPI_Comm* as c_void_p
            for _ in range(len(arg) - 1):
                # NOTE: cover with pointer decleration
                t = c.POINTER(t)
            c_args.append(t)
        c_args.append(c.c_void_p)  # MPI_Comm *
        c_func.argtypes = c_args
        c_func.errcheck = _handle_metis_ret
        setattr(cls, fname, c_func)
        _all.append(fname)
        # NOTE: mutable default behavior
        return _all


class _Lib32ParMetisModule(_LibParMetisModule):
    # 32 bit
    def __new__(cls):
        return super().__new__(cls, "parmetis")


class _Lib64ParMetisModule(_LibParMetisModule):
    _IDX_T = c.c_int64

    def __new__(cls):
        return super().__new__(cls, "parmetis64")


# pylint: disable=no-member
_libparmetis = _Lib32ParMetisModule()
_libparmetis64 = _Lib64ParMetisModule()
try:
    import sys

    # NOTE: add "modules"
    sys.modules["mgmetis.parmetis.libparmetis"] = _libparmetis
    sys.modules["mgmetis.parmetis.libparmetis64"] = _libparmetis64
finally:
    del sys


def _get_libparmetis(dtype):
    # helper to get the underlying C METIS libraries with proper integer type
    if (dtype.alignment >> 2) & 1:
        # 4 byte
        return _libparmetis
    return _libparmetis64


__default_int32_options__ = np.zeros(5, dtype=np.int32)
"""Raw data for default option values for 32bit ParMETIS"""

__default_int64_options__ = np.zeros(5, dtype=np.int64)
"""Raw data for default option values for 64bit ParMETIS"""


def _get_default_raw_opts(kw, dtype):
    # Helper function to extract options (if exists) from user input
    # or return the raw default one
    opts = kw.get("options", None)
    opts = np.asarray(
        opts
        if opts is not None
        else (
            __default_int32_options__.copy()
            if dtype == np.int32
            else __default_int64_options__.copy()
        ),
        dtype=dtype,
    )
    assert opts.size >= 4, "option length needs to be greater than 4 for ParMETIS"
    return opts


def part_kway(nparts, xadj, adjncy, vtxdist=None, comm=None, **kw):
    """Parallel partition with Kway and potentially geometry support

    .. note::
        This routine wraps two ParMETIS interfaces, namely 1)
        ``ParMETIS_V3_PartKway`` and ``ParMETIS_V3_PartGeomKway``.

    Parameters
    ----------
    nparts : int
        Number of partitions
    xadj : np.ndarray
        Local range of CSR graph starting position array
    adjncy : np.ndarray
        Local potion of CSR adjacent list with global indices
    vtxdist : np.ndarray, optional
        Global range array, see ParMETIS manual section 4.2.1, if not specified
        then will compute using MPI collection
    comm : MPI_Comm, optional
        MPI communicator, if not specified, then will use MPI_COMM_WORLD and
        try to initialize MPI via `mpi4py`.
    options : np.ndarray
        Control parameter array, see the manual 4.2.4

    Returns
    -------
    edgecuts : int
        Number of edge cuts for this process
    part : np.ndarray
        Local partition array of the local graph.

    Other Parameters
    -----------------
    vwgt, adjwgt : np.ndarray, optional
        Weighting for nodes and edges, see manual 4.2.1
    ncon : int, optional
        This is used to specify the number of weights that each vertex has. It
        is also the number of balance constraints that must be satisfied. The
        default value is 1
    tpwgts, ubvec : np.ndarray, optional
        See the manual
    par_debug : bool, optional
        Flag controling whether or not to perform a collection debugging
        actions to ensure the consistencies between weighting and numbering.
        Default is False.
    xyz : np.ndarray, optional
        If provided, then it's must be 2D array of coordinates, which are stored
        in a point-by-point fashion. The second dimension must be either 2 (2D)
        or 3 (3D). In addition, if it's specified, then this routine will call
        ``PartGeomKway`` instead of ``PartKway``.
    part : np.ndarray, optional
        User buffer for `part`.
    """
    if nparts <= 0:
        raise ValueError("invalid partition number")
    xadj, adjncy, nv = process_graph(xadj, adjncy)
    comm = get_comm(comm)  # NOTE: we initialize MPI here (if needed)
    vtxdist = np.asarray(
        vtxdist if vtxdist is not None else build_proc_dist(nv, comm, xadj[0]),
        dtype=xadj.dtype,
    )
    if vtxdist.size <= comm.size:
        raise ValueError("invalid vtxdist size, must be comm.size+1")
    vwgt = try_get_input_array(kw, "vwgt", nv, xadj.dtype)
    adjwgt = try_get_input_array(kw, "adjwgt", xadj[-1] - xadj[0], xadj.dtype)
    wgtflag = determine_wgtflag(vwgt, adjwgt)
    numflag = xadj[0]
    if kw.get("par_debug", False) and is_par(comm):
        # debug numflags
        flags = comm.allgather(numflag)
        if not np.all([x == xadj[0] for x in flags]):
            raise ValueError("inconsistent numflags {} across processes".format(flags))
        flags = comm.allgather(wgtflag)
        if not np.all([x == wgtflag for x in flags]):
            raise ValueError("inconsistent wgtflags {} accross processes".format(flags))
    ncon = kw.get("ncon", 1)
    assert ncon >= 1
    tpwgts = try_get_input_array(kw, "tpwgts", ncon * nparts, np.float32)
    if tpwgts is None:
        tpwgts = np.ones(ncon * nparts, dtype=np.float32) / nparts
    ubvec = try_get_input_array(kw, "ubvec", ncon, np.float32)
    if ubvec is None or isinstance(ubvec, float):
        try:
            ubvec = float(ubvec)
        except TypeError:
            ubvec = 1.05
        ubvec = np.asarray([ubvec] * ncon, dtype=np.float32)
    opts = _get_default_raw_opts(kw, xadj.dtype)
    # NOTE: handle geometry partition, assume 2D for the helper
    xyz = try_get_input_array(kw, "xyz", nv * 2, np.float32)
    # check size of xzy
    lib = _get_libparmetis(xadj.dtype)
    idx_t = lib._IDX_T
    nparts, ncon, numflag, wgtflag, edgecut = (
        idx_t(nparts),
        idx_t(ncon),
        idx_t(numflag),
        idx_t(wgtflag),
        idx_t(0),
    )
    part = get_or_create_workspace(kw, "part", nv, xadj.dtype)
    if xyz is None:
        # regular Kway
        lib.PartKway(
            as_pointer(vtxdist),
            as_pointer(xadj),
            as_pointer(adjncy),
            as_pointer(vwgt),
            as_pointer(adjwgt),
            c.byref(wgtflag),
            c.byref(numflag),
            c.byref(ncon),
            c.byref(nparts),
            as_pointer(tpwgts),
            as_pointer(ubvec),
            as_pointer(opts),
            c.byref(edgecut),
            as_pointer(part),
            comm_ptr(comm),
        )
    else:
        # NOTE: geometric Kway
        if xyz.ndim != 2:
            raise ValueError("coordinate must be 2D array")
        if len(xyz) < nv:
            raise ValueError("not enough coordinates")
        ndims = idx_t(xyz.shape[1])
        lib.PartGeomKway(
            as_pointer(vtxdist),
            as_pointer(xadj),
            as_pointer(adjncy),
            as_pointer(vwgt),
            as_pointer(adjwgt),
            c.byref(wgtflag),
            c.byref(numflag),
            c.byref(ndims),
            as_pointer(xyz),
            c.byref(ncon),
            c.byref(nparts),
            as_pointer(tpwgts),
            as_pointer(ubvec),
            as_pointer(opts),
            c.byref(edgecut),
            as_pointer(part),
            comm_ptr(comm),
        )
    return edgecut.value, part


def part_geom(xyz, vtxdist=None, comm=None, **kw):
    """Pure geometry based partitioning, not recommended

    .. note::
        A keyword argument `dtype` can be passed in to specify the kernel,
        the default backend is int32.

    Returns
    -------
    part : np.ndarray
        Partition array
    """
    xyz = np.asarray(xyz, dtype=np.float32)
    if xyz.ndim != 2:
        raise ValueError("coordinates must be 2D array")
    if xyz.shape[1] not in (2, 3):
        raise ValueError("must be either 2D or 3D")
    comm = get_comm(comm)  # NOTE: we initialize MPI here (if needed)
    nv = len(xyz)
    dtype = np.dtype(kw.get("dtype", np.int32))
    vtxdist = np.asarray(
        vtxdist if vtxdist is not None else build_proc_dist(nv, comm, 0), dtype=dtype
    )
    if vtxdist.size <= comm.size:
        raise ValueError("invalid vtxdist size, must be comm.size+1")
    lib = _get_libparmetis(dtype)
    ndims = lib._IDX_T(xyz.shape[1])
    part = get_or_create_workspace(kw, "part", nv, dtype)
    lib.PartGeom(
        as_pointer(vtxdist),
        c.byref(ndims),
        as_pointer(xyz),
        as_pointer(part),
        comm_ptr(comm),
    )
    return part


def part_mesh_kway(nparts, *cells, **kw):
    """K-way partitioning of a mesh in parallel

    .. note:: This routine wraps on top of ``ParMETIS_V3_PartMeshKway``.

    Parameters
    ----------
    nparts : int
        Number of partitions
    *cells : positional parameters
        Mesh, see the serial routine for more information
    elmdist : np.ndarray, optional
        Cross processing element distance array, similar to `vtxdist`
    comm : MPI_Comm, optional
        MPI communicator, default is MPI_COMM_WORLD
    opts : np.ndarray, optional
        User control parameters, see the manual

    Returns
    -------
    edgecut : int
        Edge cuts
    part : np.ndarray
        Partitioning array

    Other Parameters
    ----------------
    elmwgt : np.ndarray, optional
        This array stores the weights of the elements. See section 4.2.3
    ncon, ncommonnodes : int, optional
        See the documentation
    tpwgts, ubvec : np.ndarray, optional
        See the documentation
    part : np.ndarray, optional
        User input buffer for `part`.

    See Also
    --------
    part_kway
    """
    if nparts <= 0:
        raise ValueError("invalid nparts")
    eptr, eind, _ = process_mesh(*cells, nv=1)  # XXX: put nv=1 for dummy
    comm = get_comm(kw.get("comm", None))  # NOTE: we initialize MPI here (if needed)
    elmdist = kw.get("elmdist", None)
    elmdist = np.asarray(
        elmdist
        if elmdist is not None
        else build_proc_dist(eptr.size - 1, comm, eptr[0]),
        dtype=eptr.dtype,
    )
    if elmdist.size <= comm.size:
        raise ValueError("invalid elmdist size, must be comm.size+1")
    elmwgt = try_get_input_array(kw, "elmwgt", eptr.size - 1, eptr.dtype)
    ncon = kw.get("ncon", 1)
    assert ncon >= 1
    tpwgts = try_get_input_array(kw, "tpwgts", ncon * nparts, np.float32)
    if tpwgts is None:
        tpwgts = np.ones(ncon * nparts, dtype=np.float32) / nparts
    ubvec = try_get_input_array(kw, "ubvec", ncon, np.float32)
    if ubvec is None or isinstance(ubvec, float):
        try:
            ubvec = float(ubvec)
        except TypeError:
            ubvec = 1.05
        ubvec = np.asarray([ubvec] * ncon, dtype=np.float32)
    opts = _get_default_raw_opts(kw, eptr.dtype)
    lib = _get_libparmetis(eptr.dtype)
    idx_t = lib._IDX_T
    nparts, ncon, numflag, wgtflag, ncommonnodes, edgecut = (
        idx_t(nparts),
        idx_t(ncon),
        idx_t(eptr[0]),
        idx_t(0 if elmwgt is None else 2),
        idx_t(1),
        idx_t(0),
    )
    part = get_or_create_workspace(kw, "part", eptr.size - 1, eptr.dtype)
    # call C
    lib.PartMeshKway(
        as_pointer(elmdist),
        as_pointer(eptr),
        as_pointer(eind),
        as_pointer(elmwgt),
        c.byref(wgtflag),
        c.byref(numflag),
        c.byref(ncon),
        c.byref(ncommonnodes),
        c.byref(nparts),
        as_pointer(tpwgts),
        as_pointer(ubvec),
        as_pointer(opts),
        c.byref(edgecut),
        as_pointer(part),
        comm_ptr(comm),
    )
    return edgecut.value, part
