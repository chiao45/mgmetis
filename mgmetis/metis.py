# -*- coding: utf-8 -*-
"""Serial METIS Python interface

.. module:: mgmetis.metis
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""

import ctypes as c

from .utils import get_so, METIS_ERRORS


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
        return _all  # take advantage of mutable input behavior


class _Lib32MetisModule(_LibMetisModule):
    # 32 bit
    def __new__(cls):
        return super().__new__(cls, "metis")


class _Lib64MetisModule(_LibMetisModule):
    _IDX_T = c.c_int64

    def __new__(cls):
        return super().__new__(cls, "metis64")


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
    if (dtype.alignment >> 2) - 1:
        # 8 byte
        return _libmetis64
    return _libmetis


def _create_int(lib, v=0):
    """Helper function to create an integer with potentially default value
    """
    return lib._IDX_T(v)


def part_graph_recursize(*args):
    pass


def part_graph_kway(*args):
    pass


def part_mesh_nodal(*args):
    pass


def part_mesh_dual(*args):
    pass
