from odin.config.environment import set_hermod_logging
from odin.hermod.interfaces import IMatlab
from pymatlab.matlab import MatlabSession

'''
Session module provides tools for Hermod to run programs in different
interpretors.
'''


class GEMMatlab(IMatlab):
    """Runs matlab at gemm"""

    def start_matlab(self):
        self.m_session = MatlabSession('/opt/MATLAB/R2013a','/opt/MATLAB/R2013a/bin/matlab')       
        self.m_alive = True
        return True

    def close_matlab(self):
        self.m_alive = False
        return True

    def matlab_is_open(self):
        return self.m_alive

    def matlab_command(self,command,timeout=900):
        self.m_session.run(command)
        return self.m_session.buf[:]


