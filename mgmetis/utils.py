# -*- coding: utf-8 -*-
"""Utility functions

.. module:: mgmetis.utils
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""


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


METIS_ERRORS = {-2: MetisInputError, -3: MetisMemoryError, -4: MetisError}
"""A exception factory for handling C Metis calls

Examples
--------

>>> ret = 1  # METIS_OK
>>> try:
...     raise METIS_ERRORS[1]("meh")
... except KeyError:
...     pass
"""
