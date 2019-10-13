# -*- coding: utf-8 -*-
"""Serial METIS Python interface

.. module:: mgmetis.metis
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""

import ctypes as c

import numpy as np

from .utils import get_so, METIS_ERRORS, process_mesh


def _handle_metis_ret(ret, func, args):
    try:
        raise METIS_ERRORS[ret]("{}:{}:{}".format(func.__name__, ret, args))
    except KeyError:
        # NOTE: METIS_OK
        pass


class _LibMetisModule:
    _IDX_T = c.c_int32

    def __new__(cls, lib):
        so_obj = c.CDLL(get_so(lib))
        instance = super().__new__(cls)
        try:
            instance.__setup(so_obj)
        finally:
            # NOTE: make sure shared object is closed
            del so_obj
        return instance

    @classmethod
    def __setup(cls, so_obj):
        # PartGraphRecursive
        cls.__set_metis_func(
            so_obj, "PartGraphRecursive", ["i*"] * 8 + ["f*"] * 2 + ["i*"] * 3
        )
        # PartGraphKway
        cls.__set_metis_func(
            so_obj, "PartGraphKway", ["i*"] * 8 + ["f*"] * 2 + ["i*"] * 3
        )
        # MeshToDual
        cls.__set_metis_func(so_obj, "MeshToDual", ["i*"] * 6 + ["i**"] * 2)
        # MeshToNodal
        cls.__set_metis_func(so_obj, "MeshToNodal", ["i*"] * 5 + ["i**"] * 2)
        # PartMeshNodal
        cls.__set_metis_func(so_obj, "PartMeshNodal", ["i*"] * 7 + ["f*"] + ["i*"] * 4)
        # PartMeshDual
        cls.__set_metis_func(so_obj, "PartMeshDual", ["i*"] * 8 + ["f*"] + ["i*"] * 4)
        # NodeND
        cls.__set_metis_func(so_obj, "NodeND", ["i*"] * 7)
        # Free
        cls.__set_metis_func(so_obj, "Free", ["v"])  # v for void*
        # SetDefaultOptions
        cls.__set_metis_func(so_obj, "SetDefaultOptions", ["i*"])
        # NodeNDP
        cls.__set_metis_func(so_obj, "NodeNDP", ["i"] + ["i*"] * 3 + ["i"] + ["i*"] * 4)
        # ComputeVertexSeparator
        cls.__set_metis_func(so_obj, "ComputeVertexSeparator", ["i*"] * 7)
        # NodeRefine NOTE: last one
        _all = cls.__set_metis_func(so_obj, "NodeRefine", ["i"] + ["i*"] * 5 + ["f"])
        # NOTE: add __all__ to support `from mgmetis.metis.libmetis import *`
        setattr(cls, "__all__", _all)

    @classmethod
    def __set_metis_func(
        cls, so_obj, fname, args, _all=[]
    ):  # pylint: disable=dangerous-default-value
        # load c function
        c_func = so_obj["METIS_{}".format(fname)]
        c_func.restype = c.c_int  # integer return
        c_args = []
        for arg in args:
            t = cls._IDX_T if arg.startswith("i") else c.c_float
            if arg.startswith("v"):
                assert len(arg) == 1, "void must be point for METIS_Free"
                t = c.c_void_p
            for _ in range(len(arg) - 1):
                # NOTE: cover with pointer decleration
                t = c.POINTER(t)
            c_args.append(t)
        c_func.argtypes = c_args
        c_func.errcheck = _handle_metis_ret
        setattr(cls, fname, c_func)
        _all.append(fname)
        return _all  # XXX: take advantage of mutable input behavior


class _Lib32MetisModule(_LibMetisModule):
    # 32 bit
    def __new__(cls):
        return super().__new__(cls, "metis")


class _Lib64MetisModule(_LibMetisModule):
    _IDX_T = c.c_int64

    def __new__(cls):
        return super().__new__(cls, "metis64")


# pylint: disable=no-member
_libmetis = _Lib32MetisModule()  # 32bit module
_libmetis64 = _Lib64MetisModule()  # 64bit module
try:
    import sys

    # NOTE: add "modules"
    sys.modules["mgmetis.metis.libmetis"] = _libmetis
    sys.modules["mgmetis.metis.libmetis64"] = _libmetis64
finally:
    del sys


def _get_libmetis(dtype):
    # helper to get the underlying C METIS libraries with proper integer type
    if (dtype.alignment >> 2) & 1:
        # 4 byte
        return _libmetis
    return _libmetis64


def _array_ptr(ar, ct):
    # helper to get the pointer of an array
    # NOTE: None is NULL pointer
    return ar.ctypes.data_as(c.POINTER(ct)) if ar is not None else None


def get_default_opts(dtype="intc"):
    dtype = np.dtype(dtype)
    if not np.issubdtype(dtype, np.integer):
        raise ValueError("dtype must be integer")
    if not dtype.alignment < 4:
        raise ValueError("integer type must be int32 or int64")
    # NOTE: METIS_NOPTIONS=40
    lib = _get_libmetis(dtype)
    opts = np.empty(40, dtype=dtype)
    lib.SetDefaultOptions(opts.ctypes.data_as(c.POINTER(lib._IDX_T)))
    return opts


def part_graph_recursize(*args):
    pass


def part_graph_kway(*args):
    pass


def part_mesh_nodal(cells, nparts, **kw):
    if nparts <= 0:
        raise ValueError("invalid nparts")
    nv = kw.get("nv", -1)
    if nv == 0:
        raise ValueError("cannot be empty mesh")
    eptr, eind, nv = process_mesh(cells, nv)
    vwgt = vsize = tpwgts = None
    opts = np.asarray(
        kw.get("options", None) or get_default_opts(eptr.dtype), dtype=eptr.dtype
    )
    lib = _get_libmetis(eptr.dtype)
    idx_t = lib._IDX_T
    ne, nv, nparts, objval = (idx_t(eptr.size - 1), idx_t(nv), idx_t(nparts), idx_t(0))
    npart = np.empty(nv, dtype=eptr.dtype)
    epart = np.empty(ne, dtype=eptr.dtype)
    lib.PartMeshNodal(
        c.byref(ne),
        c.byref(nv),
        _array_ptr(eptr, idx_t),
        _array_ptr(eind, idx_t),
        _array_ptr(vwgt, idx_t),
        _array_ptr(vsize, idx_t),
        c.byref(nparts),
        _array_ptr(tpwgts, c.c_float),
        _array_ptr(opts, idx_t),
        c.byref(objval),
        _array_ptr(epart, idx_t),
        _array_ptr(npart, idx_t),
    )
    return objval.value, epart, npart


def part_mesh_dual(cells, nparts, ncommon=1, **kw):
    if nparts <= 0:
        raise ValueError("invalid nparts")
    nv = kw.get("nv", -1)
    if nv == 0:
        raise ValueError("cannot be empty mesh")
    eptr, eind, nv = process_mesh(cells, nv)
    vwgt = vsize = tpwgts = None
    opts = np.asarray(
        kw.get("options", None) or get_default_opts(eptr.dtype), dtype=eptr.dtype
    )
    lib = _get_libmetis(eptr.dtype)
    idx_t = lib._IDX_T
    ne, nv, nparts, ncommon, objval = (
        idx_t(eptr.size - 1),
        idx_t(nv),
        idx_t(nparts),
        idx_t(ncommon),
        idx_t(0),
    )
    npart = np.empty(nv, dtype=eptr.dtype)
    epart = np.empty(ne, dtype=eptr.dtype)
    lib.PartMeshDual(
        c.byref(ne),
        c.byref(nv),
        _array_ptr(eptr, idx_t),
        _array_ptr(eind, idx_t),
        _array_ptr(vwgt, idx_t),
        _array_ptr(vsize, idx_t),
        c.byref(ncommon),
        c.byref(nparts),
        _array_ptr(tpwgts, c.c_float),
        _array_ptr(opts, idx_t),
        c.byref(objval),
        _array_ptr(epart, idx_t),
        _array_ptr(npart, idx_t),
    )
    return objval.value, epart, npart
