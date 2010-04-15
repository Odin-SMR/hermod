from scipy.integrate import odeint
from scipy.interpolate import splmake, spleval,spline
import numpy as n
from pylab import interp

def intatm(z,T,newz,normz,normrho):

    wn2=0.78084 # mixing ratio N2
    wo2=0.209476 #mixing ratio O2
    Ro=8.3143 # ideal gas constant
    k=1.38054e-23 # jK-1 Boltzmans constant
    m0=28.9644
    
    def intermbar(z):
        Mbars = n.r_[28.9644, 28.9151, 28.73, 28.40, 27.88, 27.27, 26.68, 26.20, 25.80, 25.44, 25.09, 24.75, 24.42, 24.10]
        Mbarz=n.arange(85,151,5)
        m=interp(z,Mbarz,Mbars)
        return m    

    def g(z):
        Re=6372;  
        g=9.81*(1-2*z/Re)
        return g   
    
    def func(y,z,xk,cval,k):
        grad=spleval((xk,cval,k),z)
        return grad
    
    newT=spline(z,T,newz)
    mbar_over_m0=intermbar(newz)/m0
    splinecoeff=splmake(newz,g(newz)/newT*mbar_over_m0,3)
    integral=odeint(func,0,newz,splinecoeff)
    integral=3.483*n.squeeze(integral.transpose())
    integral=(1*newT[1]/newT*mbar_over_m0*n.exp(-integral))
    print integral.shape, newz.shape    
    normfactor=normrho/spline(newz,integral,normz)
    rho=normfactor*integral
    nodens=rho/intermbar(newz)*6.02282e23/1e3
    n2=wn2*mbar_over_m0*nodens
    o2=nodens*(mbar_over_m0*(1+wo2)-1)
    o=2*(1-mbar_over_m0)*nodens
    o[o<0]=0
    p=nodens*1e4*k*newT
    return newT,p,rho,nodens,n2,o2,o

