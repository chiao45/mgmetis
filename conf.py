# -*- coding: utf-8 -*-

import os
import glob
from os.path import join
from setuptools import Extension
from Cython.Build import cythonize

try:
    import mpi4py
except (ModuleNotFoundError, ImportError):
    mpi4py = None


def is_debug():
    flag = os.environ.get("MGMETIS_DEBUG", None)
    if flag is None:
        return False
    return flag.lower() not in ("0", "no", "off", "false")


debug = is_debug()

_metis_incs = [
    "mgmetis",
    join("mgmetis", "src", "metis", "GKlib"),
    join("mgmetis", "src", "metis", "include"),
    join("mgmetis", "src", "metis", "libmetis"),
]
_metis_src = []
_metis_src += glob.glob(join("mgmetis", "src", "metis", "libmetis", "*.c"))
_metis_src += glob.glob(join("mgmetis", "src", "metis", "GKlib", "*.c"))
exts = []
exts += [
    Extension(
        "mgmetis._cython.metis",
        [join("mgmetis", "_cython", "metis.pyx")] + _metis_src,
        include_dirs=_metis_incs,
    ),
    Extension(
        "mgmetis._cython.metis64",
        [join("mgmetis", "_cython", "metis64.pyx")] + _metis_src,
        include_dirs=_metis_incs,
        define_macros=[("IDXTYPEWIDTH", "64")],
    ),
]

# check MPI support
if mpi4py is not None:
    import sysconfig

    # NOTE: get rid of libmetis
    _parmetis_incs = _metis_incs[:-1] + [
        join("mgmetis", "src", "include"),
        join("mgmetis", "src", "libparmetis"),
        mpi4py.get_include(),
    ]
    _parmetis_src = glob.glob(join("mgmetis", "src", "libparmetis", "*.c"))
    # NOTE: library linking is resolved in build_ext
    exts += [
        Extension(
            "mgmetis._cython.parmetis",
            [join("mgmetis", "_cython", "parmetis.pyx")] + _parmetis_src,
            include_dirs=_parmetis_incs,
        ),
        Extension(
            "mgmetis._cython.parmetis64",
            [join("mgmetis", "_cython", "parmetis64.pyx")] + _parmetis_src,
            include_dirs=_parmetis_incs,
            define_macros=[("IDXTYPEWIDTH", "64")],
        ),
    ]
    # set compiler
    os.environ["CC"] = mpi4py.get_config()["mpicc"]
    # set linker to mpi
    os.environ["LDSHARED"] = " ".join(
        [mpi4py.get_config()["mpicc"]]
        + sysconfig.get_config_var("LDSHARED").split()[1:]
    )

_opts = {"language_level": 3}
if not debug:
    _opts.update({"wraparound": False, "boundscheck": False})
exts = cythonize(exts, compiler_directives=_opts)
