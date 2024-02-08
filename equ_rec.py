#%%
#from locale import normalize
import numpy as np
from numpy import *
import numpy.linalg as la
import numpy.polynomial as poly
#------------------
# cameras
#------------------
class EquRec:
    def bilinear(num,den,a,b,c,d):
    #compute numy(y),deny(y), such as numy(y)/deny(y) =num[(a.y+b)/(c.y+d)]/den[(a.y+b)/(c.y+d)]    
        deg_num=len(num)-1
        deg_den=len(den)-1
        max_degree=max(deg_num,deg_den)
        ayb=poly.Polynomial([b,a])
        cyd=poly.Polynomial([d,c])
        payb_i=poly.Polynomial(coef=[1])
        pcyd_o_i_=poly.Polynomial(coef=[1])
        numy=poly.Polynomial([0])
        deny=poly.Polynomial([0])
        pcyd_o_i=[0]*(max_degree+1) 
        for i in range(max_degree+1):
            pcyd_o_i[max_degree-i]=pcyd_o_i_
            pcyd_o_i_=pcyd_o_i_*cyd
        for i in range(max_degree+1):
            if (i<=deg_num): 
                numi=num[i]*payb_i*pcyd_o_i[i]
                numy=numy+numi
            if (i<=deg_den): 
                deni=den[i]*payb_i*pcyd_o_i[i]
                deny=deny+deni
            payb_i=payb_i*ayb
        numy_coef=numy.coef
        deny_coef=deny.coef

        return numy_coef,deny_coef
    def normalize( coefs, norma):
        coefs=np.asarray(coefs)/norma
        coefs=coefs.tolist()
        return coefs
    def c2d_tustin(nump,denp,Te):
        numz,denz=EquRec.bilinear(nump,denp,2/Te,-2/Te,1,1) #F(z)=F(p=[ 2/TE z-2/TE)]/[ z+1)])
        norma=denz[-1]  
        numz=EquRec.normalize(numz,norma)
        denz=EquRec.normalize(denz,norma)
        return numz,denz
    def d2c_tustin(numz,denz,Te):
        nump,denp=EquRec.bilinear(numz,denz,Te/2,1,-Te/2,1) #F(p)=F(z=[ 2/TE p +1 )]/[ -Te/2 p +1)])
        norma=denp[-1]  
        nump=EquRec.normalize(nump,norma)
        denp=EquRec.normalize(denp,norma)
        return nump,denp

    def __init__(self,  numP=[1],denP=[1],Tech=0.01):
        self.Tech=Tech
        self.outputRateIsLimited=False
        self.outputIsLimited=False
        self.numZ,self.denZ = EquRec.c2d_tustin(numP,denP,Tech) # approx tustin in z with normalization to 1 of coef denom of highest degree in z
        self.numP,self.denP=EquRec.d2c_tustin(self.numZ,self.denZ,Tech) # come back to p with normalization to 1 of coef denom of highest degree in p
        self.numz_1,self.denz_1=EquRec.bilinear(self.numZ,self.denZ,0,1,1,0)    # z=1/q = (0.q+1)/(1.q+0)
        norma=self.denz_1[0]  
        self.numz_1=np.array(EquRec.normalize(self.numz_1,norma))
        self.denz_1=np.array(EquRec.normalize(self.denz_1,norma))

        self.order=max(len(self.numZ),len(self.denZ))-1
        self.memSn=np.array([0.0]*256)  #memories of size 256, hope it is enough
        self.memEn=np.array([0.0]*256)  #memories of size 256, hope it is enough
        self.coefsAR=-self.denz_1[1:self.order+1]
        self.coefsMA=self.numz_1

        self.k=0
    def setOutputLimits(self,minOutput=-1e9,maxOutput=1e9):
        self.minOutput=minOutput
        self.maxOutput=maxOutput
        self.outputIsLimited=True    
    def setOutputRateLimits(self,minOutputRate=-1e9,maxOutputRate=1e9):
        self.maxDeltaOutputByTech=maxOutputRate*self.Tech
        self.minDeltaOutputByTech=minOutputRate*self.Tech
        self.outputRateIsLimited=True    

    def oneStep(self,en):
        # compute AR part
        k=self.k
        o=self.order
        arPart=np.dot(self.memSn[k:k+o],self.coefsAR)  #ma Part=sum(-ai.sn-i), from i=1..
        #update memories
        lastSn=self.memSn[k]
        k=k-1
        if k==-1:
            k=255-o
            self.memSn[k+1:256]=self.memSn[0:o]
            self.memEn[k+1:256]=self.memEn[0:o]
        self.memEn[k]=en
        maPart=np.dot(self.memEn[k:k+o+1],self.coefsMA) #ma Part=sum(bi.en-i), from i=0..
        self.k=k
        sn=maPart+arPart

        if self.outputRateIsLimited:
             sn=min(sn,lastSn+self.maxDeltaOutputByTech)
             sn=max(sn,lastSn+self.minDeltaOutputByTech)
        if self.outputIsLimited:
            sn=min(sn,self.maxOutput)
            sn=max(sn,self.minOutput)     
        self.memSn[k]=sn
        self.sn=sn

        return self.sn
testeEquRec=False
if testeEquRec:
    Te=0.01 
    nump=[1] #N(p)= 1+p
    denP=poly.Polynomial([1,1])
    denp= denP.coef
    print('D(p)=',denp)
    equ=EquRec(nump,denp,Te)
    equ.setOutputLimits(0.1,0.4)
    equ.setOutputRateLimits(-0.5,0.5)
    e= [1]*100
    k=0
    for en in e:
        sn=equ.oneStep(en)
        print('step ',k,' en=', en ,'sn=' ,sn)
        k=k+1 

