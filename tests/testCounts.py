import camb
import numpy as np
from scipy import special

import matplotlib.pyplot as plt
import sys, os, platform, time
from szCounts import Constants,CosmoParams,SZ_Cluster_Model,Halo_MF

from orphics.tools.output import Plotter


c = Constants()
cp = CosmoParams(constants=c)
SZProfExample = SZ_Cluster_Model(cosmoParams=cp,rms_noise = 1.,fwhm=1.5,M=5e14,z=0.5 )

zz = 0.5
MM= 5e14
print "y_m",SZProfExample.Y_M(MM,zz)




SZProfExample.plot_noise()

pars = camb.CAMBparams()
pars.set_cosmology(H0=cp.h0, ombh2=cp.ob*(cp.h0/100.)**2, omch2=(cp.om - cp.ob)*(cp.h0/100.)**2,)    
results = camb.get_background(pars)

HMF = Halo_MF(cosmoParams=cp,cambResults=results)


DA_z = results.angular_diameter_distance(zz) * (cp.h0/100.)
R500 = SZProfExample.R500
thetc = R500/DA_z

#dell = 1
#ells = np.arange(2,20000,dell)
#ktest = 10**(np.arange(-3.5,1.0,0.1))

arc = 5.9



#thetc = np.deg2rad(arc / 60.)
thetc2 = np.deg2rad(arc/2. / 60.)
print "thetc = ", thetc

el, nltemp, cl = SZProfExample.tot_noise_spec()

dell = 100
ells = np.arange(2,60000,dell)
nl = np.interp(ells,el,nltemp)
start = time.time()
y2dt2= SZProfExample.y2D_tilde_norm(ells,thetc)
print "Time for norm ", time.time() - start


plt.figure()
plt.plot(ells,nl,'--')
plt.loglog(ells,y2dt2)
plt.plot(ells,y2dt2/nl)
#plt.loglog(ells,y2dt2_2)

#FIX
#fvar = SZProf.filter_variance(thetc)
#print fvar #UNITS!!!!!!! [armin2] dropped a deg to arcmin somewhere
#print fvar * thetc**2


dthttest = np.deg2rad(0.1/60)
tht = np.arange(dthttest,60*5*dthttest,dthttest)
#tht2 = tht/2.0
#dthttest = 0.00001*arc
#tht = np.arange(dthttest,0.05*arc,dthttest)
filt = 0.0*tht
#filt2 = 0.0*tht

start2 = time.time()
for ii in xrange(len(tht)):
    filt[ii] = np.sum(special.jv(0,ells*tht[ii])*ells*y2dt2/nl)*dell
#    filt2[ii] = np.sum(special.jv(0,ells*tht[ii])*ells*y2dt2_2/nl)
print "Time for filt ", time.time() - start2

#arc = 5.9
#thetc = np.deg2rad(arc / 60.)

pars = camb.CAMBparams()
pars.set_cosmology(H0=cp.h0, ombh2=cp.ob*(cp.h0/100.)**2, omch2=(cp.om - cp.ob)*(cp.h0/100.)**2,)    
results = camb.get_background(pars)
DA_z = results.angular_diameter_distance(zz) * (cp.h0/100.)

start2 = time.time()
print np.sqrt(SZProfExample.filter_variance(DA_z))
print "Time for var " , time.time() - start2
#plt.figure()
#plt.loglog(ktest,y2dt2/y2dt2_2)

#print y2dt2/y2dt2_2
fig = plt.figure(figsize=(10,10))
plt.xlim([0,10])
#plt.plot(tht/thetc,filt/np.max(filt))

plt.plot(np.rad2deg(tht)*60.,filt/np.max(filt),'k')
#plt.plot(np.rad2deg(tht*thetc2)*60.,filt2/np.max(filt2))
plt.plot(np.rad2deg(tht)*60.,SZProfExample.y2D_norm(tht/thetc),'k--')
#plt.plot(np.rad2deg(tht)*60.,SZProf.y2D_norm(tht),'--')
#plt.plot(np.rad2deg(tht)*60.,SZProf.y2D_test(tht,thetc),'--')
plt.plot([0,10],[0,0],'k--')
#xx,yy = np.loadtxt('/Users/nab/Desktop/Projects/Match_filter/JBM_2005.dat',unpack=True)
#plt.plot(xx,yy,'rx')


# In[4]:

zmin = 0.2
zmax = 0.3
delz = (zmax-zmin)/2.
zbin_temp = np.arange(zmin,zmax,delz)
zbin = np.insert(zbin_temp,0,0.0)
start3 = time.time()

dvdz = HMF.dVdz(zbin)
dndm = HMF.N_of_z_SZ(zbin)

print "Time for N of z " , time.time() - start3


# In[ ]:

plt.plot(zbin[1:], dndm * dvdz[1:])


np.savetxt('output/dndm_dVdz_1muK_3_0arc.txt',np.transpose([zbin[1:],dndm,dvdz[1:]]))


# In[ ]:

# dtht = 0.00001
# thta = np.arange(dtht,10*thetc,dtht)
# ans = ktest
# y2D_use = SZProfExample.y2D_norm(thta/thetc)
# #for ii in xrange(len(k)):
# ii = 9000
# print ktest[ii]
# figure()
# plt.plot(thta,thta*special.jv(0,ktest[ii]*thta/thetc)*y2D_use)
# #ans[ii] = np.sum(tht*special.jv(0,k[ii]*thta/thtc)*y2D_use)*dtht

# print np.sum(thta*special.jv(0,ktest[ii]*thta/thetc)*y2D_use)*dtht

# print 2*np.pi*np.sum(SZProfExample.y2D_norm(tht/thetc)*tht)*dthttest * (180. / np.pi)**2
# print 3.42501068855e-07 * (180. / np.pi)**2


# In[ ]:



