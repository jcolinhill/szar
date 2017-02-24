import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import cPickle as pickle
import numpy as np

gridList = sys.argv[1:-1]
outName = sys.argv[-1]

print gridList
print outName

assert outName[-3:]!=".py"

grids = {}
mmins = []
mmaxes = []
zmins = []
zmaxes = []
dms = []
dzs = []

from orphics.tools.output import Plotter
pl = Plotter(labelX="$z$",labelY="S/N per cluster",ftsize=14)

for gridFile,ls,lab in zip(gridList,['-','--'],['CMB lensing','optical lensing']):

    filen = "data/"+gridFile+".pkl"
    
    mexpgrid,zgrid,errgrid = pickle.load(open(filen,'rb'))

    mmin = mexpgrid[0]
    mmax = mexpgrid[-1]
    zmin = zgrid[0]
    zmax = zgrid[-1]

    grids[gridFile] = (mexpgrid,zgrid,errgrid)

    mmins.append(mmin)
    mmaxes.append(mmax)
    zmins.append(zmin)
    zmaxes.append(zmax)
    dms.append(min(np.diff(mexpgrid)))
    dzs.append(min(np.diff(zgrid)))

    sngrid = 1./errgrid
    
    # pgrid = np.rot90(sngrid)
    # pl = Plotter(labelX="$\\mathrm{log}_{10}(M)$",labelY="$z$",ftsize=14)
    # pl.plot2d(pgrid,extent=[mmin,mmax,zmin,zmax],levels=[1.0,3.0,5.0],labsize=14)
    # pl.done("output/"+gridFile+".png")

    pl.add(zgrid,sngrid[np.where(np.isclose(mexpgrid,14.0)),:].ravel(),ls=ls,label=lab+" 10^14 Msol/h")
    pl.add(zgrid,sngrid[np.where(np.isclose(mexpgrid,14.3)),:].ravel(),ls=ls,label=lab+" 10^14.3 Msol/h")
    pl.add(zgrid,sngrid[np.where(np.isclose(mexpgrid,14.5)),:].ravel(),ls=ls,label=lab+" 10^14.5 Msol/h")
    pl.add(zgrid,sngrid[np.where(np.isclose(mexpgrid,14.7)),:].ravel(),ls=ls,label=lab+" 10^14.7 Msol/h")
    plt.gca().set_color_cycle(None)



outmgrid = np.arange(min(mmins),max(mmaxes),min(dms))
outzgrid = np.arange(min(zmins),max(zmaxes),min(dzs))
from orphics.analysis.flatMaps import interpolateGrid

jointgridsqinv = 0.
for key in grids:

    inmgrid,inzgrid,inerrgrid = grids[key]
    outerrgrid = interpolateGrid(inerrgrid,inmgrid,inzgrid,outmgrid,outzgrid,regular=False,kind="cubic",bounds_error=False,fill_value=np.inf)

    mmin = outmgrid[0]
    mmax = outmgrid[-1]
    zmin = outzgrid[0]
    zmax = outzgrid[-1]

    # from orphics.tools.output import Plotter
    # pgrid = np.rot90(1./outerrgrid)
    # pl = Plotter(labelX="$\\mathrm{log}_{10}(M)$",labelY="$z$",ftsize=14)
    # pl.plot2d(pgrid,extent=[mmin,mmax,zmin,zmax],levels=[1.0,3.0,5.0],labsize=14)
    # pl.done("output/"+key+".png")


    jointgridsqinv += (1./outerrgrid**2.)


jointgrid = np.sqrt(1./jointgridsqinv)

# sngrid = 1./jointgrid
# lab = "joint"
# pl.add(outzgrid,sngrid[np.where(np.isclose(outmgrid,14.0)),:].ravel(),ls=ls,label=lab+" 10^14 Msol/h")
# pl.add(outzgrid,sngrid[np.where(np.isclose(outmgrid,14.3)),:].ravel(),ls=ls,label=lab+" 10^14.3 Msol/h")
# pl.add(outzgrid,sngrid[np.where(np.isclose(outmgrid,14.5)),:].ravel(),ls=ls,label=lab+" 10^14.5 Msol/h")
# pl.add(outzgrid,sngrid[np.where(np.isclose(outmgrid,14.7)),:].ravel(),ls=ls,label=lab+" 10^14.7 Msol/h")

pl.legendOn(loc='upper right',labsize=8)
pl.done("output/slice.pdf")


from orphics.tools.output import Plotter
pgrid = np.rot90(1./jointgrid)
pl = Plotter(labelX="$\\mathrm{log}_{10}(M)$",labelY="$z$",ftsize=14)
pl.plot2d(pgrid,extent=[mmin,mmax,zmin,zmax],levels=[1.0,3.0,5.0],labsize=14)
pl.done("output/joint.png")

# tmgrid = np.arange(mmin,mmax,0.5)
# tzgrid = np.arange(zmin,zmax,0.5)
# coarsegrid = interpolateGrid(jointgrid,outmgrid,outzgrid,tmgrid,tzgrid,regular=False,kind="cubic",bounds_error=False,fill_value=np.inf)

# from orphics.tools.output import Plotter
# pgrid = np.rot90(1./coarsegrid)
# pl = Plotter(labelX="$\\mathrm{log}_{10}(M)$",labelY="$z$",ftsize=14)
# pl.plot2d(pgrid,extent=[mmin,mmax,zmin,zmax],levels=[1.0,3.0,5.0],labsize=14)
# pl.done("output/coarse.png")


# pickle.dump((tmgrid,tzgrid,coarsegrid),open("data/testGrid.pkl",'wb'))
