MGMETIS---Mesh & Graph METIS Partitioning
=========================================

.. image:: https://travis-ci.org/chiao45/mgmetis.svg?branch=master
    :target: https://travis-ci.org/chiao45/mgmetis
.. image:: https://img.shields.io/pypi/v/mgmetis.svg?branch=master
    :target: https://pypi.org/project/mgmetis/
.. image:: https://img.shields.io/pypi/pyversions/mgmetis.svg?style=flat-square
    :target: https://pypi.org/project/mgmetis/
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

Introduction
------------

*mgmetis* is a mesh and graph Partitioning suite wrapped on top of
`METIS & ParMETIS <http://glaros.dtc.umn.edu/gkhome/views/metis>`_. It targets
at intermediate level of package developers who work in, e.g., finite element
libraries.

*mgmetis* provides all functionalities from original METIS/ParMETIS via 1) a
`Cython <https://cython.org/>`_ interface and 2) a native Python interface
through ``ctypes``.

Installation
------------

*mgmetis* can be installed via ``pip``, i.e.,

.. code:: console

    $ pip3 install mgmetis --user

If you have MPI and `mpi4py <https://bitbucket.org/mpi4py/mpi4py/src/master/>`_
installed, then the parallel components will be built automatically. Note that
mpi4py is **NOT** an installation dependency.

Examples
--------

It's worth noting that *mgmetis* simply wraps around original METIS interfaces.
*mgmetis* doesn't have complicated data structures for graphs and meshes,
everything is passed in as arrays as per CSR format. The variable names are
preserved as what they are in the original documentation. For more information,
please refer to http://glaros.dtc.umn.edu/gkhome/metis/metis/download and
http://glaros.dtc.umn.edu/gkhome/metis/parmetis/download for METIS and ParMETIS
original documentation PDF files, respectively.

Python Mode
```````````

For graph Partitioning, either *multilevel recursive bisection* or
*multilevel k-way partitioning* methods, the interfaces are exactly the same.
The mandatory parameters are ``nparts`` (number of partitions), ``xadj`` (the
starting positions of adjacent list) and ``adjncy`` (the compressed adjacent
list).

Give a a directed graph based on the following structure::

    0---1---2
    |   |   |
    3---4---5
    |   |   |
    6---7---8

We can have the set up a simple graph representation, which looks like

.. code-block:: python

    >>> graph = {
    ...    0: [1, 3],
    ...    1: [0, 2, 4],
    ...    2: [1, 5],
    ...    3: [0, 4, 6],
    ...    4: [1, 3, 5, 7],
    ...    5: [2, 4, 8],
    ...    6: [3, 7],
    ...    7: [4, 6, 8],
    ...    8: [5, 7],
    ... }


We can then convert it into CSR graph

.. code-block:: python

    >>> xadj = [0]
    >>> for edges in graph.values():
    ...     xadj.append(xadj[-1]+len(edges))
    ...
    >>> xadj
    [0, 2, 5, 7, 10, 14, 17, 19, 22, 24]
    >>> adjncy = [node for edges in graph.values() for node in edges]

Then a partition of 2 with recursive algorithm can be simply done via

.. code-block:: python

    >>> from mgmetis import metis
    >>> objval, part = metis.part_graph_recursive(2, xadj, adjncy)
    >>> part
    array([0, 0, 1, 0, 0, 1, 1, 1, 1])

Notice that the structure in this example can also be viewed as a mesh with 12
bar cells, of which the user may want to determine a element-wise partition.

.. code-block:: python

    cells = [
    ...     [0, 1],
    ...     [1, 2],
    ...     [3, 4],
    ...     [4, 5],
    ...     [6, 7],
    ...     [7, 8],
    ...     [0, 3],
    ...     [1, 4],
    ...     [2, 5],
    ...     [3, 6],
    ...     [4, 7],
    ...     [5, 8],
    ... ]

Then, partitoning the mesh into 2 components can be done via `part_mesh_dual`

.. code-block:: python

    >>> objval, epart, npart = metis.part_mesh_dual(2, cells)
    >>> epart
    array([0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1])

For other supported advanced features, such as weights, please consult the
METIS documentation. All the arguments are supported via keyword inputs. Here,
we further demonstrate how to customize options, a.k.a. control parameters, in
METIS. The parameters in metis are specified via a fixed length 40 integer
array.

.. code-block:: python

    >>> opts = metis.get_default_options()
    >>> opts
    Options([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
             -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
             -1, -1, -1, -1, -1, -1, -1, -1], dtype=int32)

If you are familiar with METIS, you can directly work with the parameters.
*mgmetis* implements a helper module ``mgmetis.enums`` to help the user work
with control parameters. Let's say the user has a Fortran-based index graph

.. code-block:: python

    >>> from mgmetis.enums import OPTION
    >>> opts[OPTION.NUMBERING] = 1
    >>> xadj = [x + 1 for x in xadj]
    >>> adjncy = [x + 1 for x in adjncy]
    >>> objval, part = metis.part_graph_recursive(2, xadj, adjncy, options=opts)
    >>> part
    array([1, 1, 2, 1, 1, 2, 2, 2, 2])

.. note:: *mgmetis* can automatically handle Fortran index.

``ctypes`` Mode
```````````````

A powerful feature of *mgmetis* is that it allows the user to directly work
with the underlying C functions through ``ctypes``. However, by dealing with
foreign C interfaces, the user needs to explicitly ensure the type consistency.

*mgmetis* supports both 32-bit and 64-bit integer builds of METIS. The original
METIS functions all have prefix ``METIS_``, whereas in *mgmetis* ``ctypes``
module, the prefix is trimmed out. Let's see the following example to see how
to use the ``ctypes`` interface.

.. code-block:: python

    >>> import numpy as np
    >>> xadj = np.asarray(xadj)  # from list of ints, the dtype is int64
    >>> adjncy = np.asarray(adjncy)
    >>> part = np.empty(xadj.size - 1, dtype=int) # output
    >>> opts = np.assarray(opts, dtype=int)

Recall that the graph partitioning routine takes all arguments as their
references. This can be done via ``ctypes``

.. code-block:: python

    >>> import ctypes as c
    >>> nv = c.c_int64(part.size)
    >>> ncon = c.c_int64(1)
    >>> objval = c.c_int64(0)  # output
    >>> nparts = c.c_int64(2)
    >>> xadj_ptr = xadj.ctypes.data_as(c.POINTER(c.c_int64))
    >>> adj_ptr = adjncy.ctypes.data_as(c.POINTER(c.c_ind64))
    >>> opts_ptr = opts.ctypes.data_as(c.POINTER(c.c_int64))
    >>> part_ptr = part.ctypes.data_as(c.POINTER(c.c_int64))  # output address

We now need to access the ctype interface in *mgmetis*

.. code-block:: python

    >>> from mgmetis.metis import libmetis64  # libmetis for 32bit int
    >>> libmetis64.PartGraphRecursive(
    ...     c.byref(nv),
    ...     c.byref(ncon),
    ...     xadj_ptr,
    ...     adj_ptr,
    ...     None, # NULL
    ...     None,
    ...     None,
    ...     c.byref(nparts),
    ...     None,
    ...     None,
    ...     opts_ptr,
    ...     c.byref(objval),
    ...     part_ptr,
    ... )

For more details for ``ctypes``, please refer to https://docs.python.org/3.8/library/ctypes.html.
Also, take a look at `np.ndarray.ctypes <https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.ctypes.html>`_.

Enable METIS in Cython
```````````````````````

Each of the METIS routine has a Cython interface, whose naming convention is
samilar as it's in ``ctypes`` mode. *mgmetis* resolves the issues regarding
linking to METIS. In addition, each of the Cython function is defined with
``nogil`` specifier.

The following code shows how to access the ``METIS_PartGraphRecursive``

.. code-block:: cython

    cimport mgmetis.libmetis as metis  # 32 bit
    # then each of the function in METIS public domain has a Cython interface
    # without prefix METIS_
    cdef int ret = metis.PartGraphRecursive(...)
    if ret != metis.OK:
        raise ValueError

When you compile your Cython code, you don't need to worry about linking to
METIS, Python will load the correct symbol in runtime.

Work with MPI
`````````````

The native Python mode supports parallel partitioning of a static graph or
mesh. The underlying routines are:

1. ``ParMETIS_V3_PartKway``,
2. ``ParMETIS_V3_PartGeomKway``,
3. ``ParMETIS_V3_PartGeom``, and
4. ``ParMETIS_V3_PartMeshKway``.

Their usage is similar to the serial version, please take a look at the unit
testing scripts.

A complete support of ParMETIS can be done (for now) via either ``ctypes``
mode or Cython mode. For ``ctypes`` mode

.. code-block:: python

    from mgmetis.parmetis import libparmetis  # libparmetis64 for 64bit
    help(libparmetis)

and for the Cython mode

.. code-block:: cython

    cimport mgmetis.parmetis as parmetis  # mgmetis.parmetis64 for 64 bit
    cdef int ret = parmetis.PartKway(...)

Notice that for Cython mode, you will need to access *mpi4py* Cython interface.
It will, then, require you to add its path during specifying ``Extension``, and
the compiler needs to be set to *mpicc*.

License
-------

*mgmetis* is considerred as a wrapper of METIS, and it is distributed under MIT
license. Users should also refer to http://glaros.dtc.umn.edu/gkhome/views/metis
for the licenses of METIS and ParMETIS.
