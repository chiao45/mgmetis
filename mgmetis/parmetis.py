# -*- coding: utf-8 -*-
"""Parallel interface of METIS, ParMETIS

.. module:: mgmetis.parmetis
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""

import ctypes as c

from .utils import get_so, _handle_metis_ret


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
