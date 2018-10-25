import numpy as np
from szar.counts import ClusterCosmology
from configparser import ConfigParser
from orphics.io import dict_from_section,list_from_config
from szar.clustering import Clustering
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from configparser import SafeConfigParser
sns.set()

INIFILE = "input/pipeline.ini"
expName = 'S4-1.0-CDT'
gridName = 'grid-owl2'
version = '0.7'

Config = SafeConfigParser()
Config.optionxform=str
Config.read(INIFILE)
clttfile = Config.get('general','clttfile')
constDict = dict_from_section(Config,'constants')

fparams = {}
for (key, val) in Config.items('params'):
    if ',' in val:
        param, step = val.split(',')
        fparams[key] = float(param)
    else:
        fparams[key] = float(val)

cc = ClusterCosmology(fparams,constDict,clTTFixFile=clttfile)

clst = Clustering(INIFILE,expName,gridName,version,cc)

def test_ps_tilde_interpol(cc):
    mus = np.array([0])
    ks = cc.HMF.kh
    zs = cc.HMF.zarr

    fine_zs = np.linspace(zs[0], zs[-1], 1000)

    try:
        ps_interps = cc.ps_tilde_interpol(fine_zs, mus)
    except Exception as e:
        print("Test of ps_tilde_interpol failed at clustering.tilde_interpol")
        print(e)
        return

    expected = np.empty((ks.size, fine_zs.size, mus.size))
    if ps_interps.shape != expected.shape:
        print("ps_tilde_interpol shape is not the expected value; test failed!")
        sys.exit()
    else:
        print("Tests of ps_tilde_interpol passed! (Check the plots though)")

    coarse_ps_tils = cc.ps_tilde(mus)

    plt.plot(zs, coarse_ps_tils[0,:,:], marker='o', label="coarse")
    plt.plot(fine_zs, ps_interps[0,:,:], label="interp\'d")
    #plt.xscale('log')
    #plt.yscale('log')
    plt.xlabel(r'$z_\ell$')
    plt.ylabel(r'$\tilde P(z_\ell, k=k_{min})$')
    plt.legend(loc='best')
    plt.savefig('ps_tilde_interpols_test.svg')

    plt.gcf().clear()

def test_fine_ps_bar(cc, nsamps):
    mus = np.array([0])
    ks = cc.HMF.kh
    zs = cc.HMF.zarr

    try:
        fine_ps_bars = cc.fine_ps_bar(mus, nsamps)
    except Exception as e:
        print("Test of fine_ps_bar failed at clustering.fine_ps_bars")
        print(e)
        return

    expected = np.empty((ks.size, zs.size - 2, mus.size))
    if fine_ps_bars.shape != expected.shape:
        print("fine_ps_bar shape is not the expected value; test failed!")
        return
    else:
        print("Tests of fine_ps_bar passed! (Check the plots though)")

    coarse_ps_bar = cc.ps_bar(mus)

    def _ps_bar_integrand(finer_zs, mus):
        dvdz = cc.dVdz_fine(finer_zs)
        ntils = cc.ntilde_interpol(finer_zs)
        ps_tils = cc.ps_tilde_interpol(finer_zs, mus)
        prefac = dvdz * ntils**2
        prefac = prefac[..., np.newaxis]
        return prefac * ps_tils

    plt.plot(zs, coarse_ps_bar[0,:,0], marker='o', label="coarse")
    plt.plot(zs[1:-1], fine_ps_bars[0,:,0], marker='.', label="fine")
    plt.xlabel(r'$z_\ell$')
    plt.ylabel(r'$\bar P(z_\ell, \mu = 0, k=m_{min})$')
    plt.legend(loc='best')
    plt.savefig('fine_ps_bars_test_nsamps{}.svg'.format(nsamps))

    plt.gcf().clear()

    plt.plot(ks, coarse_ps_bar[:,1,0], label="coarse")
    plt.plot(ks, fine_ps_bars[:,0,0], label="fine")
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(r'$k$')
    plt.ylabel(r'$\bar P(z = z_{min+1}, \mu = 0, k)$')
    plt.legend(loc='best')
    plt.savefig('fine_ps_bars_kspace_nsamps{}.svg'.format(nsamps))

    plt.gcf().clear()

    finer_zs = np.linspace(zs[1], zs[-1], 10*nsamps)
    integrand = _ps_bar_integrand(finer_zs, mus)

    plt.plot(finer_zs, integrand[0, :, 0])
    plt.xlabel(r'$z$')
    plt.ylabel(r'$dV/dz \, \tilde n^2 \tilde P$')
    plt.savefig('fine_ps_bar_integrand_test_nsamps{}.svg'.format(nsamps))

    plt.gcf().clear()

def test_fine_sfunc(cc):
    mus = np.array([0])
    ks = cc.HMF.kh
    zs = cc.HMF.zarr
    zs_noends = zs[1:-1]

    try:
        fine_sfunc_vals = cc.fine_sfunc(1000)
    except Exception as e:
        print("Test of fine_sfunc failed at clustering.fine_sfunc")
        print(e)
        sys.exit()

    expected = zs_noends
    if fine_sfunc_vals.shape != expected.shape:
        print("fine_sfunc_vals shape is not the expected value; test failed!")
        sys.exit()
    else:
        print("Tests of fine_sfunc passed! (Check the plots though)")

    coarse_sfunc_vals = cc.Norm_Sfunc()

    plt.plot(zs, 10*coarse_sfunc_vals, marker='o', label="coarse")
    plt.plot(zs_noends, 10*fine_sfunc_vals, marker='.', label="fine")
    plt.plot(zs_noends, coarse_sfunc_vals[1:-1]/fine_sfunc_vals, marker='.', label="ratio")
    #plt.xscale('log')
    #plt.yscale('log')
    plt.xlabel(r'$z_\ell$')
    plt.ylabel(r'$10 \times S(z_\ell)$')
    plt.legend(loc='upper center')
    plt.savefig('fine_sfunc_test.svg')

    plt.gcf().clear()

def test_ps_tilde(cc):
    mus = np.linspace(0,1, 50)
    ks = cc.HMF.kh
    zs = cc.HMF.zarr
    try:
        pstildes = cc.ps_tilde(mus)
    except Exception as e:
        print("Test of ps_tilde failed at clustering.ps_tilde")
        print(e)
        return

    expected = np.empty((ks.size, zs.size, mus.size))

    if pstildes.shape != expected.shape:
        print("ps_tilde shape is not the expected value; test failed!")
        return
    else:
        print("Tests of ps_tilde passed!")

if __name__ == '__main__':
    test_fine_sfunc(clst)
    test_ps_tilde(clst)
    test_ps_tilde_interpol(clst)
    nsamps = 100
    test_fine_ps_bar(clst, nsamps)