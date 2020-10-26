# execute simulation script with all TOLERANCE combinations

######################################################################################
# very important: linSol, nonLinSolIter, solAlg must be their corresponding integers #
#                                                                                    #
# linSol:           Dense == 1  GMRES == 6  BiCGStab == 7   SPTFQMR == 8    KLU == 9 #
# nonLinSolIter:    Functional == 1     Newton-type == 2                             #
# solAlg:           Adams == 1      BDF == 2                                         #
#                                                                                    #
######################################################################################

from SimAllSettings import *
from tqdm import trange


# settings
atol = [1e-6, 1e-8, 1e-10, 1e-12, 1e-14, 1e-16]
rtol = [1e-6, 1e-8, 1e-10, 1e-12, 1e-14, 1e-16]
linSol = 9
iter = 2
solAlg = [1,2]
maxStep = 10000
# just for the tolerance study containing different combinations, don't change!
study_indicator = 2

# run simulation
for iSolALg in trange(0, len(solAlg)):
    for iAtol in trange(0, len(atol)):
        for iRtol in trange(0, len(rtol)):
            simulate(
                atol[iAtol],
                rtol[iRtol],
                linSol,
                iter,
                solAlg[iSolALg],
                maxStep,
                study_indicator)
            useless_variable = os.system('clear')
            pass
