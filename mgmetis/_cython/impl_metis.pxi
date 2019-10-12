# -*- coding: utf-8 -*-

# NOTE: we enforce include from src/ so that we know we include the METIS
# comes with mgmetis

cdef extern from "src/metis/include/metis.h" nogil:
    int METIS_PartGraphRecursive(idx_t *nvtxs, idx_t *ncon, idx_t *xadj, 
                  idx_t *adjncy, idx_t *vwgt, idx_t *vsize, idx_t *adjwgt, 
                  idx_t *nparts, real_t *tpwgts, real_t *ubvec, idx_t *options, 
                  idx_t *edgecut, idx_t *part)

    int METIS_PartGraphKway(idx_t *nvtxs, idx_t *ncon, idx_t *xadj, 
                  idx_t *adjncy, idx_t *vwgt, idx_t *vsize, idx_t *adjwgt, 
                  idx_t *nparts, real_t *tpwgts, real_t *ubvec, idx_t *options, 
                  idx_t *edgecut, idx_t *part)

    int METIS_MeshToDual(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind, 
                  idx_t *ncommon, idx_t *numflag, idx_t **r_xadj, idx_t **r_adjncy)

    int METIS_MeshToNodal(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind, 
                  idx_t *numflag, idx_t **r_xadj, idx_t **r_adjncy)

    int METIS_PartMeshNodal(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *vwgt, idx_t *vsize, idx_t *nparts, real_t *tpwgts, 
                  idx_t *options, idx_t *objval, idx_t *epart, idx_t *npart)

    int METIS_PartMeshDual(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *vwgt, idx_t *vsize, idx_t *ncommon, idx_t *nparts, 
                  real_t *tpwgts, idx_t *options, idx_t *objval, idx_t *epart, 
                  idx_t *npart)

    int METIS_NodeND(idx_t *nvtxs, idx_t *xadj, idx_t *adjncy, idx_t *vwgt,
                  idx_t *options, idx_t *perm, idx_t *iperm)

    int METIS_Free(void *ptr)

    int METIS_SetDefaultOptions(idx_t *options)

    int METIS_NodeNDP(idx_t nvtxs, idx_t *xadj, idx_t *adjncy, idx_t *vwgt,
                   idx_t npes, idx_t *options, idx_t *perm, idx_t *iperm, 
                   idx_t *sizes)

    int METIS_ComputeVertexSeparator(idx_t *nvtxs, idx_t *xadj, idx_t *adjncy, 
                   idx_t *vwgt, idx_t *options, idx_t *sepsize, idx_t *part)

    int METIS_NodeRefine(idx_t nvtxs, idx_t *xadj, idx_t *vwgt, idx_t *adjncy,
                   idx_t *where, idx_t *hmarker, real_t ubfactor)


cdef int PartGraphRecursive(idx_t *nvtxs, idx_t *ncon, idx_t *xadj,
                  idx_t *adjncy, idx_t *vwgt, idx_t *vsize, idx_t *adjwgt,
                  idx_t *nparts, real_t *tpwgts, real_t *ubvec, idx_t *options,
                  idx_t *edgecut, idx_t *part) nogil:
    return METIS_PartGraphRecursive(nvtxs, ncon, xadj, adjncy, vwgt, vsize,
        adjwgt, nparts, tpwgts, ubvec, options, edgecut, part)


cdef int PartGraphKway(idx_t *nvtxs, idx_t *ncon, idx_t *xadj,
                  idx_t *adjncy, idx_t *vwgt, idx_t *vsize, idx_t *adjwgt,
                  idx_t *nparts, real_t *tpwgts, real_t *ubvec, idx_t *options,
                  idx_t *edgecut, idx_t *part) nogil:
    return METIS_PartGraphKway(nvtxs, ncon, xadj, adjncy, vwgt, vsize, adjwgt, 
        nparts, tpwgts, ubvec, options, edgecut, part)


cdef int MeshToDual(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *ncommon, idx_t *numflag, idx_t **r_xadj,
                  idx_t **r_adjncy) nogil:
    return METIS_MeshToDual(ne, nn, eptr, eind, ncommon, numflag, r_xadj, r_adjncy)


cdef int MeshToNodal(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *numflag, idx_t **r_xadj, idx_t **r_adjncy) nogil:
    return METIS_MeshToNodal(ne, nn, eptr, eind, numflag, r_xadj, r_adjncy)


cdef int PartMeshNodal(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *vwgt, idx_t *vsize, idx_t *nparts, real_t *tpwgts,
                  idx_t *options, idx_t *objval, idx_t *epart, idx_t *npart) nogil:
    return METIS_PartMeshNodal(ne, nn, eptr, eind, vwgt, vsize, nparts, tpwgts,
        options, objval, epart, npart)


cdef int PartMeshDual(idx_t *ne, idx_t *nn, idx_t *eptr, idx_t *eind,
                  idx_t *vwgt, idx_t *vsize, idx_t *ncommon, idx_t *nparts,
                  real_t *tpwgts, idx_t *options, idx_t *objval, idx_t *epart,
                  idx_t *npart) nogil:
    return METIS_PartMeshDual(ne, nn, eptr, eind, vwgt, vsize, ncommon, nparts, 
        tpwgts, options, objval, epart, npart)


cdef int NodeND(idx_t *nvtxs, idx_t *xadj, idx_t *adjncy, idx_t *vwgt,
                  idx_t *options, idx_t *perm, idx_t *iperm) nogil:
    return METIS_NodeND(nvtxs, xadj, adjncy, vwgt, options, perm, iperm)


cdef int Free(void *ptr) nogil:
    return METIS_Free(ptr)


cdef int SetDefaultOptions(idx_t *options) nogil:
    return METIS_SetDefaultOptions(options)


cdef int NodeNDP(idx_t nvtxs, idx_t *xadj, idx_t *adjncy, idx_t *vwgt,
                   idx_t npes, idx_t *options, idx_t *perm, idx_t *iperm,
                   idx_t *sizes) nogil:
    return METIS_NodeNDP(nvtxs, xadj, adjncy, vwgt, npes, options, perm, iperm, sizes)


cdef int ComputeVertexSeparator(idx_t *nvtxs, idx_t *xadj, idx_t *adjncy,
                   idx_t *vwgt, idx_t *options, idx_t *sepsize, idx_t *part) nogil:
    return METIS_ComputeVertexSeparator(nvtxs, xadj, adjncy, vwgt, options,
        sepsize, part)


cdef int NodeRefine(idx_t nvtxs, idx_t *xadj, idx_t *vwgt, idx_t *adjncy,
                   idx_t *where, idx_t *hmarker, real_t ubfactor) nogil:
    return METIS_NodeRefine(nvtxs, xadj, vwgt, adjncy, where, hmarker, ubfactor)
