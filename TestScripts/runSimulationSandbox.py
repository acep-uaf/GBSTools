
from GBSModel.Operational.runSimulation import runSimulation
import sys
import os
here = os.path.dirname(os.path.realpath(__file__))
runSimulation(here + '/../GBSProjects/StMary/OutputData/Set1000')
#runSimulation(here + '/../../GBSProjects/ControlProject1/OutputData/SetBaseLine')