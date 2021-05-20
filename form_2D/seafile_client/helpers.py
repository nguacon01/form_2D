def compute(x, u):
    "given X (parameters) and U (variables) estimates y (timings)"
    nproc, si1, si2, zf1, zf2, SPG, rank, iters, didimp = u   # variables
    timprt, tFT2, tFT1, tsane, tpg, tDS, tadm = x     # model
    inisz = si1*si2
    totalsz = si1*zf1*si2*zf2
    if nproc == 1:
        np = 1
    else:
        np = (nproc - 1)
        np *= 0.98**np
    imprt = timprt*inisz
    FT2 = tFT2*inisz*zf2/np
    if SPG == 1:
        FT1 = totalsz*(tFT1 + tsane*rank*(iters+1) )/np
    elif SPG == 2:
        FT1 = totalsz*(tFT1 +  tpg*rank*(iters+1))/np
    elif SPG == 0:
        FT1 = tFT1*totalsz/np
    
    DS = tDS*totalsz
    adm = tadm*totalsz
    Total = (FT2 + FT1) + DS + adm
    if didimp == 1:
        Total += imprt
    return (imprt,FT2,FT1,DS,Total)

def predict(nproc, si1, si2, zf1, zf2, SPG, rank, iters, didimp):
    """
    predict processing time in minutes on Rosala, given
    nproc: number of processors using MPI
    si1, si2: size of data-set in k
    zf1, zf2: zerofilling levels
    SPG: optional processing 0: None, 1: SANE, 2:PGSANE
    rank, iters: parameters for SANE and PGSANE
    didimp: 0: no import, 1:import was done
    """
    Xopt = [0.00567425, 0.00153274, 0.02739466, 0.00434163, 0.0447748 , 0.00195605, 0.00543571]
    #         timprt,     tFT2,       tFT1,       tsane,      tpg,      tDS,          tadm
    # optimised 2021-03-26  on 22 values
    u = (nproc, si1, si2, zf1, zf2, SPG, rank, iters, didimp)
    val = compute(Xopt, u)[-1]
    if val<15:
        val = 15.0
    elif val < 60:
        val = 60.0
    return val