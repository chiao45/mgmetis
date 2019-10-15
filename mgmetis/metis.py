# -*- coding: utf-8 -*-
"""Serial METIS Python interface

.. module:: mgmetis.metis
.. moduleauthor:: Qiao Chen, <benechiao@gmail.com>
"""

import ctypes as c

import numpy as np

from .enums import OPTION
from .utils import (
    get_so,
    process_mesh,
    process_graph,
    as_pointer,
    get_or_create_workspace,
    try_get_input_array,
    _handle_metis_ret,
)

__all__ = [
    "get_default_options",
    "part_graph_recursize",
    "part_graph_kway",
    "part_mesh_nodal",
    "part_mesh_dual",
    "node_nd",
]


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
        return _all  # NOTE: take advantage of mutable default input behavior


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


__default_int32_options__ = -1 * np.ones(40, dtype=np.int32)
"""Raw data for default option values for 32bit METIS"""

__default_int64_options__ = -1 * np.ones(40, dtype=np.int64)
"""Raw data for default option values for 64bit METIS"""


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
    assert opts.size >= 40, "option length needs to be greater than 40"
    return opts


def get_default_options(dtype="intc"):
    """Create an array of length 40 with default option values (-1)

    Parameters
    ----------
    dtype : np.dtype, optional
        Data type, must be either np.int32 (or equiv.) or np.int64 (or equiv.)

    Returns
    -------
    np.ndarray
        An integer array of length 40 with values -1 (default METIS options)

    Notes
    -----

    The returned array is a subclass of np.ndarray with an additional member
    method `revert_default_options`, whose sole purpose is to reset all entries
    to be -1, i.e.,

    >>> opts[:] = -1

    Examples
    --------

    >>> from mgmetis import metis
    >>> opts = metis.get_default_options()
    >>> opts
    Options([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
         -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
         -1, -1, -1, -1, -1, -1, -1, -1], dtype=int32)
    >>> opts.revert_default_options()

    All interfaces of `mgmetis` accept standard np.ndarray, so you can manually
    create option arrays by

    >>> opts = -1 * np.ones(40, dtype=int)

    See Also
    --------
    enums : `mgmetis` METIS enum interface
    enums.OPTION
    """
    dtype = np.dtype(dtype)
    if not np.issubdtype(dtype, np.integer):
        raise ValueError("dtype must be integer")
    if dtype.alignment < 4:
        raise ValueError("integer type must be int32 or int64")
    # NOTE: METIS_NOPTIONS=40
    opts = np.empty(40, dtype=dtype)

    class Options(np.ndarray):
        def revert_default_options(self):
            """Revert the default options

            .. note::
                This function internally does **NOT** call
                ``METIS_SetDefaultOptions``.
            """
            self[:] = -1

    opts = opts.view(Options)  # NOTE: numpy simple subclass
    opts.revert_default_options()
    return opts


def _part_graph(kernel, nparts, xadj, adjncy, **kw):  # pylint: disable=too-many-locals
    # NOTE: unified implementation of graph partitioning
    if nparts <= 0:
        raise ValueError("invalid nparts")
    ncon = kw.get("ncon", 1)
    if ncon < 1:
        raise ValueError("invalid ncon, should be at least 1")
    xadj, adjncy, nv = process_graph(xadj, adjncy)
    vwgt = try_get_input_array(kw, "vwgt", nv * ncon, xadj.dtype)
    vsize = try_get_input_array(kw, "vsize", nv, xadj.dtype)
    adjwgt = try_get_input_array(kw, "adjwgt", xadj[-1] - xadj[0], xadj.dtype)
    tpwgts = try_get_input_array(kw, "tpwgts", nparts * ncon, np.float32)
    ubvec = try_get_input_array(kw, "ubvec", ncon, np.float32)
    opts = _get_default_raw_opts(kw, xadj.dtype)
    if xadj[0] == 1:
        # NOTE: fortran
        opts[OPTION.NUMBERING] = 1
    lib = _get_libmetis(xadj.dtype)
    idx_t = lib._IDX_T
    nv, ncon, nparts, objval = idx_t(nv), idx_t(ncon), idx_t(nparts), idx_t(0)
    part = get_or_create_workspace(kw, "part", nv.value, xadj.dtype)
    getattr(lib, kernel)(
        c.byref(nv),
        c.byref(ncon),
        as_pointer(xadj),
        as_pointer(adjncy),
        as_pointer(vwgt),
        as_pointer(vsize),
        as_pointer(adjwgt),
        c.byref(nparts),
        as_pointer(tpwgts),
        as_pointer(ubvec),
        as_pointer(opts),
        c.byref(objval),
        as_pointer(part),
    )
    return objval.value, part


def part_graph_recursize(nparts, xadj, adjncy, **kw):
    """Partition a graph into k parts with `multilevel recursive bisection`

    .. note::
        This function wraps around original ``METIS_PartGraphRecursive``. For
        more details, please refer to the official
        `documentation <http://glaros.dtc.umn.edu/gkhome/metis/metis/download>`_
        section 5.8, `Graph partitioning routines`.
        Also, be aware that most documentations are copied from the original
        source for the convenience.

    Parameters
    ----------
    nparts : int
        Number of partitions, must be positive
    xadj, adjncy: np.ndarray
        The adjacency structure (CSR) described in section 5.5 in documentation.
    options : np.ndarray, optional
        Control parameters in section 5.4. If not given, then using default
        values.
    ncon : int, optional
        The number of balancing constraints. It should be at least 1 (default).

    Returns
    -------
    objval : int
        Upon successful completion, this variable stores the edge-cut or the
        total communication volume of the partitioning solution. The value
        returned depends on the partitioning’s objective function.
    part : np.ndarray
        This is a vector of size nvtxs that upon successful completion stores
        the partition vector of the graph. The numbering of this vector starts
        from either 0 or 1, depending on the value of
        `options[OPTION.NUMBERING]`.

    Other Parameters
    ----------------
    vwgt, vsize, adjwgt : np.ndarray, optional
        See section 5.5 in the documentation, default is ``None``, indicating
        using the default behaviors inside the C routine.
    tpwgts : np.ndarray, optional
        This is an array of size nparts×ncon that specifies the desired weight
        for each partition and constraint. Default is ``None``.
    ubvec : np.ndarray, optional
        This is an array of size ncon that specifies the allowed load imbalance
        tolerance for each constraint. See the doc.

    See Also
    --------
    part_graph_kway
    """
    return _part_graph("PartGraphRecursive", nparts, xadj, adjncy, **kw)


def part_graph_kway(nparts, xadj, adjncy, **kw):
    """Partition a graph into k parts with `multilevel k-way partitioning`

    .. note::
        This function wraps around original ``METIS_PartGraphKway``. For
        more details, please refer to the official
        `documentation <http://glaros.dtc.umn.edu/gkhome/metis/metis/download>`_
        section 5.8, `Graph partitioning routines`.
        Also, be aware that most documentations are copied from the original
        source for the convenience.

    Parameters
    ----------
    nparts : int
        Number of partitions, must be positive
    xadj, adjncy: np.ndarray
        The adjacency structure (CSR) described in section 5.5 in documentation.
    options : np.ndarray, optional
        Control parameters in section 5.4. If not given, then using default
        values.
    ncon : int, optional
        The number of balancing constraints. It should be at least 1 (default).

    Returns
    -------
    objval : int
        Upon successful completion, this variable stores the edge-cut or the
        total communication volume of the partitioning solution. The value
        returned depends on the partitioning’s objective function.
    part : np.ndarray
        This is a vector of size nvtxs that upon successful completion stores
        the partition vector of the graph. The numbering of this vector starts
        from either 0 or 1, depending on the value of
        `options[OPTION.NUMBERING]`.

    Other Parameters
    ----------------
    vwgt, vsize, adjwgt : np.ndarray, optional
        See section 5.5 in the documentation, default is ``None``, indicating
        using the default behaviors inside the C routine.
    tpwgts : np.ndarray, optional
        This is an array of size nparts×ncon that specifies the desired weight
        for each partition and constraint. Default is ``None``.
    ubvec : np.ndarray, optional
        This is an array of size ncon that specifies the allowed load imbalance
        tolerance for each constraint. See the doc.

    See Also
    --------
    part_graph_recursize
    """
    return _part_graph("PartGraphKway", nparts, xadj, adjncy, **kw)


def part_mesh_nodal(nparts, *cells, **kw):  # pylint: disable=too-many-locals
    """Partition a mesh based on cutting nodes

    .. note::
        This function wraps around original ``METIS_PartMeshNodal``. For more,
        please refer to the official
        `documentation <http://glaros.dtc.umn.edu/gkhome/metis/metis/download>`_
        section 5.9, `Mesh partitioning routines`.
        Also, be aware that most documentations are copied from the original
        source for the convenience.

    Parameters
    ----------
    nparts : int
        Number of partitions, must be positive
    *cells : positional arguments
        This can be either the compressed mesh input, i.e., `eptr` and `eind`
        or a list of cells, which will be automatically converted into proper
        `eptr` and `eind` arrays. For more about the input mesh structure,
        refer to section 5.6 in the documentation.
    nv : int, optional
        Total number of vertices in mesh, if not specified or negative, then
        the routine will compute it automatically.
    options : np.ndarray, optional
        Control parameters as documented in the documentation, if not provided,
        the the default options are used. For more, see section 5.4 in the
        official documentation.

    Returns
    -------
    objval : int
        Upon successful completion, this variable stores either the edgecut or
        the total communication volume of the nodal graph’s partitioning.
    epart : np.ndarray
        This is a vector of size ne that upon successful completion stores the
        partition vector for the elements of the mesh. The numbering of this
        vector starts from either 0 or 1, depending on the value of
    npart : np.ndarray
        This is a vector of size nn that upon successful completion stores the
        partition vector for the nodes of the mesh. The numbering of this vector
        starts from either 0 or 1, depending on the value of
        `options[OPTION.NUMBERING]`.

    Other Parameters
    ----------------
    vwgt : np.ndarray, optional
        An array of size `nv` specifying the weights of the nodes. A ``None``
        value (default) can be passed to indicate that all nodes have an equal
        weight.
    vsize : np.ndarray, optional
        An array of size `nv` specifying the size of the nodes that is used for
        computing the total communication volume as described in Section 5.7.
        A ``None`` value (default) can be passed when the objective is cut or
        when all nodes have an equal size.
    tpwgts : np.ndarray, optional
        This is an array of size `nparts` that specifies the desired weight for
        each partition. The target partition weight for the `i`-th partition is
        specified at `tpwgts[i]` (the numbering for the partitions starts from
        0). `sum(tpwgts)` must be 1.0. A ``None`` value (default) can be passed
        to indicate that the graph should be equally divided among the
        partitions. Also, be aware this array is real data type.
    epart, npart : np.ndarray, optional
        User workspace of output `epart` and `npart`, respectively.

    See Also
    --------
    get_default_options
    part_mesh_dual : element-wise partitioning for a given mesh
    """
    if nparts <= 0:
        raise ValueError("invalid nparts")
    eptr, eind, nv = process_mesh(*cells, nv=kw.get("nv", -1))
    opts = _get_default_raw_opts(kw, eptr.dtype)
    if eptr[0] == 1:
        # NOTE: fortran
        opts[OPTION.NUMBERING] = 1
    lib = _get_libmetis(eptr.dtype)
    idx_t = lib._IDX_T
    ne, nv, nparts, objval = (idx_t(eptr.size - 1), idx_t(nv), idx_t(nparts), idx_t(0))
    # outputs
    npart = get_or_create_workspace(kw, "npart", nv.value, eptr.dtype)
    epart = get_or_create_workspace(kw, "epart", ne.value, eptr.dtype)
    # inputs
    vwgt = try_get_input_array(kw, "vwgt", nv.value, eptr.dtype)
    vsize = try_get_input_array(kw, "vsize", nv.value, eptr.dtype)
    tpwgts = try_get_input_array(kw, "tpwgts", nparts.value, np.float32)
    lib.PartMeshNodal(
        c.byref(ne),
        c.byref(nv),
        as_pointer(eptr),
        as_pointer(eind),
        as_pointer(vwgt),
        as_pointer(vsize),
        c.byref(nparts),
        as_pointer(tpwgts),
        as_pointer(opts),
        c.byref(objval),
        as_pointer(epart),
        as_pointer(npart),
    )
    return objval.value, epart, npart


def part_mesh_dual(nparts, *cells, **kw):  # pylint: disable=too-many-locals
    """Partition a mesh based on cutting elements

    .. note::
        This function wraps around original ``METIS_PartMeshDual``. For more,
        please refer to the official
        `documentation <http://glaros.dtc.umn.edu/gkhome/metis/metis/download>`_
        section 5.9, `Mesh partitioning routines`.
        Also, be aware that most documentations are copied from the original
        source for the convenience.

    Parameters
    ----------
    nparts : int
        Number of partitions, must be positive
    *cells : positional arguments
        This can be either the compressed mesh input, i.e., `eptr` and `eind`
        or a list of cells, which will be automatically converted into proper
        `eptr` and `eind` arrays. For more about the input mesh structure,
        refer to section 5.6 in the documentation.
    nv : int, optional
        Total number of vertices in mesh, if not specified or negative, then
        the routine will compute it automatically.
    ncommon : int, optional
        Specifies the number of common nodes that two elements must have in
        order to put an edge between them in the dual graph. Given two elements
        :math:`e_1` and :math:`e_2`, containing :math:`n_1` and :math:`n_2`
        nodes, respectively, then an edge will connect the vertices in the dual
        graph corresponding to :math:`e_1` and :math:`e_2` if the number of
        common nodes between them is greater than or equal to
        :math:`min(ncommon, n_1 − 1, n_2 − 1)`. The default value is 1,
        indicating that two elements will be connected via an edge as long as
        they share one node. However, this will tend to create too many edges
        (increasing the memory and time requirements of the partitioning). The
        user should select higher values that are better suited for the element
        types of the mesh that wants to partition. For example, for tetrahedron
        meshes, ncommon should be 3, which creates an edge between two tets when
        they share a triangular face (i.e., 3 nodes).
    options : np.ndarray, optional
        Control parameters as documented in the documentation, if not provided,
        the the default options are used. For more, see section 5.4 in the
        official documentation.

    Returns
    -------
    objval : int
        Upon successful completion, this variable stores either the edgecut or
        the total communication volume of the nodal graph’s partitioning.
    epart : np.ndarray
        This is a vector of size ne that upon successful completion stores the
        partition vector for the elements of the mesh. The numbering of this
        vector starts from either 0 or 1, depending on the value of
    npart : np.ndarray
        This is a vector of size nn that upon successful completion stores the
        partition vector for the nodes of the mesh. The numbering of this vector
        starts from either 0 or 1, depending on the value of
        `options[OPTION.NUMBERING]`.

    Other Parameters
    ----------------
    vwgt : np.ndarray, optional
        An array of size `ne` specifying the weights of the elements. A ``None``
        value (default) can be passed to indicate that all elements have an
        equal weight.
    vsize : np.ndarray, optional
        An array of size `ne` specifying the size of the elements that is used
        for computing the total communication volume as described in Section 5.7.
        A ``None`` value (default) can be passed when the objective is cut or
        when all elements have an equal size.
    tpwgts : np.ndarray, optional
        This is an array of size `nparts` that specifies the desired weight for
        each partition. The target partition weight for the `i`-th partition is
        specified at `tpwgts[i]` (the numbering for the partitions starts from
        0). `sum(tpwgts)` must be 1.0. A ``None`` value (default) can be passed
        to indicate that the graph should be equally divided among the
        partitions. Also, be aware this array is real data type.
    epart, npart : np.ndarray, optional
        User workspace of output `epart` and `npart`, respectively.

    See Also
    --------
    get_default_options
    part_mesh_nodal : node-wise partitioning for a given mesh
    """
    if nparts <= 0:
        raise ValueError("invalid nparts")
    eptr, eind, nv = process_mesh(*cells, nv=kw.get("nv", -1))
    opts = _get_default_raw_opts(kw, eptr.dtype)
    if eptr[0] == 1:
        # NOTE: fortran
        opts[OPTION.NUMBERING] = 1
    lib = _get_libmetis(eptr.dtype)
    idx_t = lib._IDX_T
    ne, nv, nparts, ncommon, objval = (
        idx_t(eptr.size - 1),
        idx_t(nv),
        idx_t(nparts),
        idx_t(kw.get("ncommon", 1)),
        idx_t(0),
    )
    # outputs
    npart = get_or_create_workspace(kw, "npart", nv.value, eptr.dtype)
    epart = get_or_create_workspace(kw, "epart", ne.value, eptr.dtype)
    # inputs
    vwgt = try_get_input_array(kw, "vwgt", ne.value, eptr.dtype)
    vsize = try_get_input_array(kw, "vsize", ne.value, eptr.dtype)
    tpwgts = try_get_input_array(kw, "tpwgts", nparts.value, np.float32)
    lib.PartMeshDual(
        c.byref(ne),
        c.byref(nv),
        as_pointer(eptr),
        as_pointer(eind),
        as_pointer(vwgt),
        as_pointer(vsize),
        c.byref(ncommon),
        c.byref(nparts),
        as_pointer(tpwgts),
        as_pointer(opts),
        c.byref(objval),
        as_pointer(epart),
        as_pointer(npart),
    )
    return objval.value, epart, npart


def node_nd(xadj, adjncy, **kw):
    """Sparse matrix reordering with nested dissection to reduce fills

    Reducing fills with by using nested dissection reordering algorithm.

    Parameters
    ----------
    xadj, adjncy : np.ndarray
        CSR graph representation of a CSR/CSC matrix
    options : np.ndarray, optional
        Control parameters, if not specified, then the default values are
        used.

    Returns
    -------
    perm : np.ndarray
        Permutation matrix :math:`P`
    iperm : np.ndarray
        Inverse permutation matrix :math:`P^T`

    Other Parameters
    ----------------
    vwgt : np.ndarray, optional
        Vertex weights, default is None, which indicates equal weights.
    perm, iperm : np.ndarray, optional
        User input of workspace for `perm` and `iperm`
    """
    xadj, adjncy, nv = process_graph(xadj, adjncy)
    vwgt = try_get_input_array(kw, "vwgt", nv, xadj.dtype)
    opts = _get_default_raw_opts(kw, xadj.dtype)
    if xadj[0] == 1:
        # NOTE: Fortran
        opts[OPTION.NUMBERING] = 1
    # outputs
    perm = get_or_create_workspace(kw, "perm", nv, xadj.dtype)
    iperm = get_or_create_workspace(kw, "iperm", nv, xadj.dtype)
    lib = _get_libmetis(xadj.dtype)
    nv = lib._IDX_T(nv)
    lib.NodeND(
        c.byref(nv),
        as_pointer(xadj),
        as_pointer(adjncy),
        as_pointer(vwgt),
        as_pointer(opts),
        as_pointer(perm),
        as_pointer(iperm),
    )
    return perm, iperm
