# -*- coding: utf-8 -*-
"""Tabulation of enumerations used in METIS

.. note::
    For more information, please consult the original documentation at
    http://glaros.dtc.umn.edu/gkhome/metis/metis/download

.. module:: mgmetis.enums
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""

from enum import IntEnum, unique, auto

__all__ = [
    "ERROR",
    "OP",
    "OPTION",
    "PTYPE",
    "GTYPE",
    "CTYPE",
    "IPTYPE",
    "RTYPE",
    "DBG",
    "OBJTYPE",
]


@unique
class ERROR(IntEnum):
    """Return status, i.e., `rstatus_et`
    """

    OK = 1
    INPUT = -2
    MEMORY = -3
    ERROR = -4


@unique
class OP(IntEnum):
    """Operation type codes, i.e., `moptions_et`
    """

    PMETIS = 0
    KMETIS = 1
    OMETIS = 2


@unique
class OPTION(IntEnum):
    """Options codes, i.e., `moptions_et`

    Examples
    --------

    >>> opts[OPTION.PTYPE] = PTYPE.RB
    """

    PTYPE = 0
    OBJTYPE = auto()
    CTYPE = auto()
    IPTYPE = auto()
    RTYPE = auto()
    DBGLVL = auto()
    NITER = auto()
    NCUTS = auto()
    SEED = auto()
    NO2HOP = auto()
    MINCONN = auto()
    CONTIG = auto()
    COMPRESS = auto()
    CCORDER = auto()
    PFACTOR = auto()
    NSEPS = auto()
    UFACTOR = auto()
    NUMBERING = auto()
    HELP = auto()
    TPWGTS = auto()
    NCOMMON = auto()
    NOOUTPUT = auto()
    BALANCE = auto()
    GTYPE = auto()
    UBVEC = auto()


@unique
class PTYPE(IntEnum):
    """Partitioning Schemes, i.e., `mptype_et`
    """

    RB = 0
    KWAY = 1


@unique
class GTYPE(IntEnum):
    """Graph types for meshes, i.e., `mgtype_et`
    """

    DUAL = 0
    NODAL = 1


@unique
class CTYPE(IntEnum):
    """Coarsening Schemes, i.e., `mctype_et`
    """

    RM = 0
    SHEM = 1


@unique
class IPTYPE(IntEnum):
    """Initial partitioning schemes, i.e., `miptype_et`
    """

    GROW = 0
    RANDOM = auto()
    EDGE = auto()
    NODE = auto()
    METISRB = auto()


@unique
class RTYPE(IntEnum):
    """Refinement schemes, i.e., `mrtype_et`
    """

    FM = 0
    GREEDY = auto()
    SEP2SIDED = auto()
    SEP1SIDED = auto()


@unique
class DBG(IntEnum):
    """Debug Levels, i.e., `mdbglvl_et`
    """

    INFO = 1
    TIME = 2
    COARSEN = 4
    REFINE = 8
    IPART = 16
    MOVEINFO = 32
    SEPINFO = 64
    CONNINFO = 128
    CONTIGINFO = 256
    MEMORY = 2048


@unique
class OBJTYPE(IntEnum):
    """Types of objectives i.e., `mobjtype_et`
    """

    CUT = 0
    VOL = 1
    NODE = 2
