###############################################################################
# plot_mapsurfdens_highalpha.py: make of plot of the surface-density of the 
#                                high alpha stars
###############################################################################
import os, os.path
import sys
import csv
import pickle
import numpy
import matplotlib
matplotlib.use('Agg')
from galpy.util import bovy_plot
from matplotlib import pyplot, cm
import densprofiles
import define_rcsample
_SKIP= 10
_SIGNIF= 0.025
def plot_mapsurfdens(plotname):
    with open('../mapfits/tribrokenexpflare.sav','rb') as savefile:
        bf= numpy.array(pickle.load(savefile))
        samples_brexp= numpy.array(pickle.load(savefile))
    plotmaps= [19,26,32,39,45]
    bovy_plot.bovy_print(fig_width=8.,fig_height=3.)
    maps= define_rcsample.MAPs()
    cmap= cm.coolwarm
    overplot= False
    Rs= numpy.linspace(4.,14.,1001)
    # Setup for saving the profiles
    csvfile= open(os.path.join('..','out','mapsurfdens_highalpha.csv'),'w')
    writer= csv.writer(csvfile,delimiter=',',quoting=csv.QUOTE_NONE)
    writer.writerow(['# Surface density profile for MAPs (Figure 11 in Bovy et al. 2016)'])
    writer.writerow(['# The first line lists the radii at which the surface density profiles'])
    writer.writerow(['# are evaluated'])
    writer.writerow(['# The rest of the file are the log surface profiles; the 0.025'])
    writer.writerow(['# lower limit and the 0.0975 upper limit (each 1 line)'])
    writer.writerow(['# Different MAPs are separated by a comment line'])
    writer.writerow(['{:.2f}'.format(x) for x in Rs])
    for ii, map in enumerate(maps.map()):
        if not ii in plotmaps: continue
        # Create all density profiles
        samples= samples_brexp[ii,:,::_SKIP]
        nsamples= len(samples[0])
        tRs= numpy.tile(Rs,(nsamples,1)).T
        ldp= numpy.empty((len(Rs),nsamples))
        Rb= numpy.tile(numpy.exp(samples[3]),(len(Rs),1))
        ihRin= numpy.tile(samples[0],(len(Rs),1))
        ihRout= numpy.tile(samples[2],(len(Rs),1))
        # Rb >= R0
        leRb= (tRs <= Rb)*(Rb >= densprofiles._R0)
        ldp[leRb]= ihRin[leRb]*(tRs[leRb]-densprofiles._R0)
        gtRb= (tRs > Rb)*(Rb >= densprofiles._R0)
        ldp[gtRb]= -ihRout[gtRb]*(tRs[gtRb]-densprofiles._R0)\
            +ihRout[gtRb]*(Rb[gtRb]-densprofiles._R0)\
            +ihRin[gtRb]*(Rb[gtRb]-densprofiles._R0)
        # Rb < R0, normalize outer at R0
        leRb= (tRs <= Rb)*(Rb < densprofiles._R0)
        ldp[leRb]= ihRin[leRb]*(tRs[leRb]-densprofiles._R0)\
            -ihRout[leRb]*(Rb[leRb]-densprofiles._R0)\
            -ihRin[leRb]*(Rb[leRb]-densprofiles._R0)
        gtRb= (tRs > Rb)*(Rb < densprofiles._R0)
        ldp[gtRb]= -ihRout[gtRb]*(tRs[gtRb]-densprofiles._R0)
        # Label and relative normalization
        tfeh= round(numpy.median(map['FE_H'])*20.)/20.
        if tfeh == 0.25: tfeh= 0.3
        if tfeh == -0.1: tfeh= -0.1
        print ii, tfeh, len(map)
        anorm= 10**(-10.*(-tfeh-0.5))
        #if (-tfeh-0.4) > 0.3: anorm= 10**(-12.*(-tfeh+0.4)) 
        if (-tfeh-0.5) == -0.2: anorm= 10**(-11.*(-tfeh-0.5))
        anorm= 1./anorm # re-order
        anorm/= 3.
        norm= numpy.exp(numpy.median(ldp,axis=1))[numpy.argmin(numpy.fabs(Rs-densprofiles._R0))]/anorm
        bovy_plot.bovy_plot(Rs,numpy.exp(numpy.median(ldp,axis=1))/norm,
                            '-',
                            color=cmap((tfeh+0.5)*0.95/0.5+0.05),
                            lw=2.,overplot=overplot,
                            ylabel=r'$\Sigma(R)\times\mathrm{constant}$',
                            xrange=[0.,16.],
                            yrange=[0.000001,90.],
                            semilogy=True)
        pyplot.fill_between(Rs,
                            numpy.exp(numpy.sort(ldp,axis=1)[:,int(round(_SIGNIF*nsamples))])/norm,
                            numpy.exp(numpy.sort(ldp,axis=1)[:,int(round((1.-_SIGNIF)*nsamples))])/norm,
                            color=cmap((tfeh+0.5)/0.4),
                            lw=0.)
        overplot= True
        if ii == 19:
            bovy_plot.bovy_text(2.,
                                10.**1.,
                                r'$[\mathrm{Fe/H}]$',size=16.,color='k')
        bovy_plot.bovy_text(2.,(numpy.exp(numpy.median(ldp,axis=1))/norm)[0],
                            r'$%+.1f$' % tfeh,size=16.,
                            color=cmap((tfeh+0.5)*0.95/0.5+0.05))
        writer.writerow(['# High-alpha MAP w/ [Fe/H]=%g' % tfeh])
        writer.writerow(['{:.3f}'.format(x) for x in list(numpy.median(ldp,axis=1))])
        writer.writerow(['{:.3f}'.format(x) for x in list(numpy.sort(ldp,axis=1)[:,int(round(_SIGNIF*nsamples))])])
        writer.writerow(['{:.3f}'.format(x) for x in list(numpy.sort(ldp,axis=1)[:,int(round((1.-_SIGNIF)*nsamples))])])
    csvfile.close()
    bovy_plot.bovy_text(10.,10.**1.,
                        r'$\mathrm{high-}[\alpha/\mathrm{Fe}]\ \mathrm{MAPs}$',
                        size=16.)
    pyplot.gca().tick_params(axis='y',which='minor',left='off',right='off')
    bovy_plot.bovy_end_print(plotname)

if __name__ == '__main__':
    plot_mapsurfdens(sys.argv[1])
    
