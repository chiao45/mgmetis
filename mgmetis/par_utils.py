# -*- coding: utf-8 -*-
"""Utility functions for parallel environment with MPI

.. module:: mgmetis.par_utils
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""

import ctypes as c

import numpy as np


def get_comm(comm):
    """Helper routine to get communicator

    Parameters
    ----------
    comm : MPI_Comm
        MPI communicator

    Returns
    -------
    MPI_Comm
        If the input communicator is None, then return the MPI_COMM_WORLD
    """
    if comm is None:
        from mpi4py import MPI

        return MPI.COMM_WORLD
    return comm


def comm_ptr(comm):
    """Get the pointer to the communicator
    """
    # see https://github.com/mpi4py/mpi4py/blob/master/demo/wrap-ctypes/helloworld.py
    comm = get_comm(comm)
    from mpi4py import MPI

    if MPI._sizeof(MPI.Comm) == c.sizeof(c.c_int):
        MPI_Comm = c.c_int
    else:
        # must be pointer
        MPI_Comm = c.c_void_p
    return c.byref(MPI_Comm.from_address(MPI._addressof(comm)))


def is_par(comm):
    """Check if or not in parallel environment
    """
    return comm and comm.size > 1


def build_proc_dist(nv, comm, start):
    """Build process-wise index distance array

    Parameters
    ----------
    nv : int
        Number of local vertices
    comm : MPI_Comm
        MPI communicator
    start : {0,1}
        Starting index

    Returns
    -------
    list
        The distance array across all processes.

    Warnings
    --------

    The caller should ensure the index system consistency for `xadj`, i.e.,
    the first entry should be either 0 or 1 and must be homogeneous for all
    processes. This routine doesn't check this!
    """
    assert start in (0, 1)
    if not is_par(comm):
        return np.asarray([start, start + nv])
    return np.asarray(np.append([start], np.cumsum(comm.allgather(nv)) + start))


def determine_wgtflag(vwgt, adjwgt):
    """Determine the wgtflag used in many parallel partitioning routines
    """
    if vwgt is None and adjwgt is None:
        return 0
    if vwgt is None:
        return 1
    return 2 if adjwgt is None else 3
