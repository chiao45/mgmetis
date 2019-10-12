# -*- coding: utf-8 -*-

from libc.stdint cimport int64_t


ctypedef int64_t idx_t
ctypedef float real_t

ctypedef enum:
    NOPTIONS = 40

cdef int PartGraphRecursive(idx_t *nvtxs, idx_t *ncon, idx_t *xadj,
                  idx_t *adjncy, idx_t *vwgt, idx_t *vsize, idx_t *adjwgt,
                  idx_t *nparts, real_t *tpwgts, real_t *ubvec, idx_t *options,
                  idx_t *edgecut, idx_t *part) nogil
cdef int PartGraphKway(idx_t *nvtxs, idx_t *ncon, idx_t *xadj,
                  idx_t *adjncy, idx_t *vwgt, idx_t *vsize, idx_t *adjwgt,
                  idx_t *nparts, real_t *tpwgts, real_t *ubvec, idx_t *options,
                  idx_t *edgecut, idx_t *part) nogil
cdef int MeshToDual(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *ncommon, idx_t *numflag, idx_t **r_xadj,
                  idx_t **r_adjncy) nogil
cdef int MeshToNodal(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *numflag, idx_t **r_xadj, idx_t **r_adjncy) nogil
cdef int PartMeshNodal(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *vwgt, idx_t *vsize, idx_t *nparts, real_t *tpwgts,
                  idx_t *options, idx_t *objval, idx_t *epart, idx_t *npart) nogil
cdef int PartMeshDual(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *vwgt, idx_t *vsize, idx_t *ncommon, idx_t *nparts,
                  real_t *tpwgts, idx_t *options, idx_t *objval, idx_t *epart,
                  idx_t *npart) nogil
cdef int NodeND(idx_t *nvtxs, idx_t *xadj, idx_t *adjncy, idx_t *vwgt,
                  idx_t *options, idx_t *perm, idx_t *iperm) nogil
cdef int Free(void *ptr) nogil
cdef int SetDefaultOptions(idx_t *options) nogil
cdef int NodeNDP(idx_t nvtxs, idx_t *xadj, idx_t *adjncy, idx_t *vwgt,
                   idx_t npes, idx_t *options, idx_t *perm, idx_t *iperm,
                   idx_t *sizes) nogil
cdef int ComputeVertexSeparator(idx_t *nvtxs, idx_t *xadj, idx_t *adjncy,
                   idx_t *vwgt, idx_t *options, idx_t *sepsize, idx_t *part) nogil
cdef int NodeRefine(idx_t nvtxs, idx_t *xadj, idx_t *vwgt, idx_t *adjncy,
                   idx_t *where, idx_t *hmarker, real_t ubfactor) nogil

# Return codes
ctypedef enum rstatus_et:
    OK              = 1
    ERROR_INPUT     = -2
    ERROR_MEMORY    = -3
    ERROR           = -4

# Operation type codes
ctypedef enum moptype_et:
    OP_PMETIS
    OP_KMETIS
    OP_OMETIS

# Options codes (i.e., options[])
ctypedef enum moptions_et:
    OPTION_PTYPE
    OPTION_OBJTYPE
    OPTION_CTYPE
    OPTION_IPTYPE
    OPTION_RTYPE
    OPTION_DBGLVL
    OPTION_NITER
    OPTION_NCUTS
    OPTION_SEED
    OPTION_NO2HOP
    OPTION_MINCONN
    OPTION_CONTIG
    OPTION_COMPRESS
    OPTION_CCORDER
    OPTION_PFACTOR
    OPTION_NSEPS
    OPTION_UFACTOR
    OPTION_NUMBERING
    OPTION_HELP
    OPTION_TPWGTS
    OPTION_NCOMMON
    OPTION_NOOUTPUT
    OPTION_BALANCE
    OPTION_GTYPE
    OPTION_UBVEC

# Partitioning Schemes
ctypedef enum mptype_et:
    PTYPE_RB
    PTYPE_KWAY

# Graph types for meshes
ctypedef enum mgtype_et:
    GTYPE_DUAL
    GTYPE_NODAL

# Coarsening Schemes
ctypedef enum mctype_et:
    CTYPE_RM
    CTYPE_SHEM

# Initial partitioning schemes
ctypedef enum miptype_et:
    IPTYPE_GROW
    IPTYPE_RANDOM
    IPTYPE_EDGE
    IPTYPE_NODE
    IPTYPE_METISRB

# Refinement schemes
ctypedef enum mrtype_et:
    RTYPE_FM
    RTYPE_GREEDY
    RTYPE_SEP2SIDED
    RTYPE_SEP1SIDED

# Debug Levels
ctypedef enum mdbglvl_et:
    DBG_INFO       = 1
    DBG_TIME       = 2
    DBG_COARSEN    = 4
    DBG_REFINE     = 8
    DBG_IPART      = 16
    DBG_MOVEINFO   = 32
    DBG_SEPINFO    = 64
    DBG_CONNINFO   = 128
    DBG_CONTIGINFO = 256
    DBG_MEMORY     = 2048

# Types of objectives
ctypedef enum mobjtype_et:
    OBJTYPE_CUT
    OBJTYPE_VOL
    OBJTYPE_NODE
