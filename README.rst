MGMETIS---Mesh & Graph METIS Partitioning
=========================================

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

Introduction
------------

`mgmetis` is a mesh and graph Partitioning suite wrapped on top of
`METIS and ParMETIS <http://glaros.dtc.umn.edu/gkhome/views/metis>`_. It targets
at intermediate level of package developers who work in, e.g., finite element
libraries.

`mgmetis` provides all functionalities from original METIS/ParMETIS via 1) a
`Cython <https://cython.org/>`_ interface and 2) a native Python interface
through ``ctypes``.

Installation
------------

`mgmetis` can be installed via ``pip``, i.e.,

.. code:: console

    $ pip3 install mgmetis --user

If you have MPI and `mpi4py <https://bitbucket.org/mpi4py/mpi4py/src/master/>`_
installed, then the parallel components will be built automatically. Note that
mpi4py is **NOT** an installation dependency.

License
-------

MIT License

Copyright (c) 2019 Qiao Chen
