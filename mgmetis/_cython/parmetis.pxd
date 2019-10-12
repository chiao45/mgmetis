# -*- coding: utf-8 -*-

from libc.stdint cimport int32_t
from mpi4py.libmpi cimport MPI_Comm


ctypedef int32_t idx_t
ctypedef float real_t

cdef int PartKway(idx_t *vtxdist, idx_t *xadj, idx_t *adjncy, idx_t *vwgt, 
	     idx_t *adjwgt, idx_t *wgtflag, idx_t *numflag, idx_t *ncon, idx_t *nparts, 
	     real_t *tpwgts, real_t *ubvec, idx_t *options, idx_t *edgecut, idx_t *part, 
	     MPI_Comm *comm) nogil
cdef int PartGeomKway(idx_t *vtxdist, idx_t *xadj, idx_t *adjncy, idx_t *vwgt, 
	     idx_t *adjwgt, idx_t *wgtflag, idx_t *numflag, idx_t *ndims, real_t *xyz, 
	     idx_t *ncon, idx_t *nparts, real_t *tpwgts, real_t *ubvec, idx_t *options, 
	     idx_t *edgecut, idx_t *part, MPI_Comm *comm) nogil
cdef int PartGeom(idx_t *vtxdist, idx_t *ndims, real_t *xyz, idx_t *part, MPI_Comm *comm) nogil
cdef int RefineKway(idx_t *vtxdist, idx_t *xadj, idx_t *adjncy, idx_t *vwgt, 
	     idx_t *adjwgt, idx_t *wgtflag, idx_t *numflag, idx_t *ncon, idx_t *nparts, 
	     real_t *tpwgts, real_t *ubvec, idx_t *options, idx_t *edgecut, 
	     idx_t *part, MPI_Comm *comm) nogil
cdef int AdaptiveRepart(idx_t *vtxdist, idx_t *xadj, idx_t *adjncy, idx_t *vwgt, 
	     idx_t *vsize, idx_t *adjwgt, idx_t *wgtflag, idx_t *numflag, idx_t *ncon, 
	     idx_t *nparts, real_t *tpwgts, real_t *ubvec, real_t *ipc2redist, 
	     idx_t *options, idx_t *edgecut, idx_t *part, MPI_Comm *comm) nogil
cdef int Mesh2Dual(idx_t *elmdist, idx_t *eptr, idx_t *eind, idx_t *numflag, 
	     idx_t *ncommonnodes, idx_t **xadj, idx_t **adjncy, MPI_Comm *comm) nogil
cdef int PartMeshKway(idx_t *elmdist, idx_t *eptr, idx_t *eind, idx_t *elmwgt, 
	     idx_t *wgtflag, idx_t *numflag, idx_t *ncon, idx_t *ncommonnodes, idx_t *nparts, 
	     real_t *tpwgts, real_t *ubvec, idx_t *options, idx_t *edgecut, idx_t *part, 
	     MPI_Comm *comm) nogil
cdef int NodeND(idx_t *vtxdist, idx_t *xadj, idx_t *adjncy, idx_t *numflag, 
	     idx_t *options, idx_t *order, idx_t *sizes, MPI_Comm *comm) nogil
cdef int V32_NodeND(idx_t *vtxdist, idx_t *xadj, idx_t *adjncy, idx_t *vwgt,
             idx_t *numflag, idx_t *mtype, idx_t *rtype, idx_t *p_nseps, idx_t *s_nseps,
             real_t *ubfrac, idx_t *seed, idx_t *dbglvl, idx_t *order, 
             idx_t *sizes, MPI_Comm *comm) nogil
cdef int SerialNodeND(idx_t *vtxdist, idx_t *xadj, idx_t *adjncy, idx_t *numflag, 
             idx_t *options, idx_t *order, idx_t *sizes, MPI_Comm *comm) nogil

# Operation type codes
ctypedef enum pmoptype_et:
    OP_KMETIS
    OP_GKMETIS
    OP_GMETIS
    OP_RMETIS
    OP_AMETIS
    OP_OMETIS
    OP_M2DUAL
    OP_MKMETIS

# Matching type
ctypedef enum:
    MTYPE_LOCAL = 1
    MTYPE_GLOBAL = 2

# Separator refinement types
ctypedef enum:
    SRTYPE_GREEDY = 1
    SRTYPE_2PHASE = 2

# Coupling types for ParMETIS_V3_RefineKway & ParMETIS_V3_AdaptiveRepart
ctypedef enum:
    PSR_COUPLED = 1
    PSR_UNCOUPLED = 2

# Debug levels (fields should be ORed)
ctypedef enum:
    DBGLVL_TIME = 1
    DBGLVL_INFO = 2
    DBGLVL_PROGRESS = 4
    DBGLVL_REFINEINFO = 8
    DBGLVL_MATCHINFO = 16
    DBGLVL_RMOVEINFO = 32
    DBGLVL_REMAP = 64
