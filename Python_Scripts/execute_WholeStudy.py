# execute simulation script with ALL solver setting combinations

######################################################################################
# very important: linSol, nonLinSolIter, solAlg must be their corresponding integers #
#                                                                                    #
# linSol:           Dense == 1  GMRES == 6  BiCGStab == 7   SPTFQMR == 8    KLU == 9 #
# nonLinSolIter:    Functional == 1     Newton-type == 2                             #
# solAlg:           Adams == 1      BDF == 2                                         #
#                                                                                    #
######################################################################################

from SimAllSettings import simulate

# settings
atol = [1e-8, 1e-6, 1e-12, 1e-10, 1e-14, 1e-16, 1e-8]
rtol = [1e-6, 1e-8, 1e-10, 1e-12, 1e-14, 1e-8, 1e-16]
linSol = [1, 6, 7, 8, 9]
iter = [1, 2]
solAlg = [1, 2]
maxStep = 10000
# for the main study, don't change!
study_indicator = 1

# run simulation
for iSolALg in range(0, len(solAlg)):
    for iNonLin in range(0, len(iter)):
        for iLinSol in range(0, len(linSol)):
            for iToleranceTupel in range(0, len(atol)):
                simulate(
                    atol[iToleranceTupel],
                    rtol[iToleranceTupel],
                    linSol[iLinSol],
                    iter[iNonLin],
                    solAlg[iSolALg],
                    maxStep,
                    study_indicator)
                pass
