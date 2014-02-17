#!/usr/bin/env /opt/env/haines/dataproc/bin/python
# Last modified:  Time-stamp: <2009-10-29 13:47:50 haines>
"""bogue_dspec_plot"""

import os, sys
import datetime, time, dateutil, dateutil.tz
import pycdf
import numpy

sys.path.append('/opt/env/haines/dataproc/raw2proc')
del(sys)

os.environ["MPLCONFIGDIR"]="/home/haines/.matplotlib/"

from pylab import figure, twinx, twiny, savefig, setp, getp, cm, colorbar
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, DateFormatter, date2num, num2date
from matplotlib.ticker import MaxNLocator, FormatStrFormatter, ScalarFormatter
import procutil

def which_to_plot(odir, ncfn):
    """
    Finds which timestamp in netCDF data file (ncfn) does not have a
    corresponding directional spectrum plot png in output dir (odir)

   :Parameters:
       odir : string, path to location of png's
       ncfn : string, filename and path to netCDF file 

   :Returns:
       j_seq : integer sequence, for indices of data to plot
       
    """

    nc = pycdf.CDF(ncFile1)
    # nc = pycdf.CDFMF((ncFile1, ncFile2))
    ncvars = nc.variables()
    # print ncvars
    es = nc.var('time')[:]
    units = nc.var('time').units
    dt = [procutil.es2dt(e) for e in es]
    dts = [d.strftime('%Y_%m_%d_%H%M') for d in dt]
    # list all pngs
    import glob
    gs = os.path.join(odir, '*.png')
    all_pngs = glob.glob(gs)
    ap = ''.join(all_pngs)
    # find index of dts not in all_pngs
    j_seq = [j for j in range(len(dts)) if ap.find(dts[j]) == -1]
    # return index values to plot (j)
    return j_seq

print 'bogue_dspec_plot ...'
prev_month, this_month, next_month = procutil.find_months(procutil.this_month())
# ncFile1='/home/haines/test_data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_2008_03.nc'
# ncFile2='/seacoos/data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_2008_03.nc'
# ncFile1='/seacoos/data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_'+prev_month.strftime('%Y_%m')+'.nc'
ncFile1='/seacoos/data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_'+this_month.strftime('%Y_%m')+'.nc'
odir = os.path.join('/seacoos/data/nccoos/level3/bogue/adcpwaves/dspec', this_month.strftime('%Y_%m'))
if not os.path.exists(odir):
    os.mkdir(odir)

j_seq = which_to_plot(odir, ncFile1)
# print j_seq

if not j_seq:
    j_seq = [-1]

# load data
print ' ... loading data for graph from ...'
print ' ... ... ' + ncFile1
# print ' ... ... ' + ncFile2
for j in j_seq:
    nc = pycdf.CDF(ncFile1)
    # nc = pycdf.CDFMF((ncFile1, ncFile2))
    ncvars = nc.variables()
    # print ncvars
    es = nc.var('time')[:]
    units = nc.var('time').units
    dt = [procutil.es2dt(e) for e in es]
    # set timezone info to UTC (since data from level1 should be in UTC!!)
    dt = [e.replace(tzinfo=dateutil.tz.tzutc()) for e in dt]
    # return new datetime based on computer local
    dt_local = [e.astimezone(dateutil.tz.tzlocal()) for e in dt]
    dn = date2num(dt)
    f = nc.var('f')[:]
    d = nc.var('d')[:]
    Sxx = nc.var('Sxx')[j]
    Sf = nc.var('Sf')[j]
    Stheta = nc.var('Stheta')[j]
    Stheta_wind = nc.var('Stheta_wind')[j]
    Stheta_swell = nc.var('Stheta_swell')[j]
    Tp = nc.var('Tp')[j]
    Tpw = nc.var('Tp_wind')[j]
    Tps = nc.var('Tp_swell')[j]
    Dp = nc.var('Dp')[j]
    Dpw = nc.var('Dp_wind')[j]
    Dps = nc.var('Dp_swell')[j]
    Hs = nc.var('Hs')[:]
    Hss = nc.var('Hs_swell')[:]
    Hsw = nc.var('Hs_wind')[:]
    nc.close()

    print '... ... ' + dt[j].strftime('%Y_%m_%d_%H%M')

    # range for pcolor plots
    cmin, cmax = (0.0, 0.05)
    # last dt in data for labels
    dt1 = dt[j]
    dt2 = dt_local[j]

    diff = abs(dt1 - dt2)
    if diff.days>0:
        last_dt_str = dt1.strftime("%H:%M %Z on %b %d, %Y") + ' (' + dt2.strftime("%H:%M %Z, %b %d") + ')'
    else:
        last_dt_str = dt1.strftime("%H:%M %Z") + ' (' + dt2.strftime("%H:%M %Z") + ')' \
                      + dt2.strftime(" on %b %d, %Y")
        
    fn_dt_str = dt1.strftime("%Y_%m_%d_%H%M")
        
    fig = figure(figsize=(9, 7))
    
    #######################################
    # full directional spectrum S(f,d)
    #######################################
    # print ' ... Sxx'
    ax = fig.add_axes((.1,.4,.4,.45))
    axs = [ax]

    # use masked array to hide NaN's on plot
    Sxxm = numpy.ma.masked_where(Sxx==0.0, Sxx)
    pc = ax.pcolor(f, d, Sxxm.T, vmin=cmin, vmax=cmax)
    # pc = ax.pcolor(f, d, Sxxm.T)
    ax.set_ylabel('Direction (deg N)')
    ax.set_ylim(0., 360.)
    l0 = ax.axvline(x=0.1, color='k', linestyle=':', linewidth=1.5)
    ax.set_xlim(0., 0.635)
    ax.set_xlabel('Frequency (Hz)')
    
    # setup colorbar axes instance.
    l,b,w,h = ax.get_position().bounds
    cax = fig.add_axes([l+w+0.025, b-0.06, 1.0*w, 0.03])
    
    cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
    cb.set_label('Spectral Density (m2/Hz/deg)')
    cb.ax.xaxis.set_label_position('top')
    # cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
    # cb.ax.set_xticklabels([-0.4, -0.2, 0, 0.2, 0.4])

    # top scale wave period
    ax2 = twiny(ax)
    ax2.set_xlim(0., 0.635)
    ax2.xaxis.tick_top()
    # convert (bottom) Hertz to (top scale) seconds (1/Hz)
    Hertz = ax.get_xticks()
    Hertz = [val for val in Hertz if val!=0 ]
    ax2.set_xticks(Hertz)
    s = [round(1./val,2) for val in Hertz]
    ax2.set_xticklabels(s)
    ax2.set_xlabel('Wave Period (sec)')
    
    #######################################
    # print ' ... all, swell, and wind labels'
    ax = fig.add_axes((.1,.875,.4,.10))
    axs.append(ax)
    
    ax.set_axis_off()
    ax.set_axis_bgcolor(None)
    ax.axvline(x=0.1, color='k', linestyle=':', linewidth=1.5)
    ax.plot([0., 0.635], [0.6, 0.6], 'k-')
    ax.plot([0.005], [0.6],'k<')
    ax.plot([0.63],[0.6],'k>')
    ax.text(0.5, 0.65, 'ALL FREQs',
            horizontalalignment='center',
            #        verticalalignment='center',
            transform=ax.transAxes,
            bbox=dict(facecolor=None, edgecolor='k', alpha=1))
    
    ax.plot([0.0, 0.1], [0.3,0.3], 'g-')
    ax.plot([0.005], [0.3],'g<')
    ax.plot([0.095],[0.3],'g>')
    ax.text(0.05, .35, 'SWELL', color='g',
            horizontalalignment='center',
            #        verticalalignment='center',
            transform=ax.transAxes,
            bbox=dict(facecolor=None, edgecolor='g', alpha=1))
    
    ax.plot([0.1, 0.635], [0.3,0.3], 'b-')
    ax.plot([0.105], [0.3], 'b<')
    ax.plot([0.63], [0.3], 'b>')
    ax.text(0.7, 0.35, 'WIND', color='b',
            horizontalalignment='center',
            #        verticalalignment='center',
            transform=ax.transAxes,
            bbox=dict(facecolor=None, edgecolor='b', alpha=1))
    ax.set_ylim(0.,1.)
    ax.set_xlim(0.,0.635)
    
    #######################################
    # print ' ... Sf'
    ax = fig.add_axes((.1,.25,.4,.15))
    axs.append(ax)
    
    l1, = ax.plot(f, Sf, 'k-')
    l1.set_label('Non-directional Spectrum')
    l0 = ax.axvline(x=0.1, color='k', linestyle=':', linewidth=1.5)
    l2 = ax.axvline(1/Tp, color='k', linestyle='-', label='ALL Wave Frequencies')
    l3 = ax.axvline(1/Tps, color='g', linestyle='-', label='SWELL Waves')
    l4 = ax.axvline(1/Tpw, color='b', linestyle='-', label='WIND Waves')
    ax.set_axis_bgcolor(None)
    ax.set_xlim(0., 0.635)
    ax.set_ylabel('Sf (m2/Hz)')
    ax.set_ylim(0, 3.0)
    # ax.set_title('Frequency Spectrum')
    
    # legend
    ls2 = l2.get_label()
    ls3 = l3.get_label()
    ls4 = l4.get_label()
    leg = fig.legend((l2,l3,l4), (ls2,ls3,ls4), loc=(.520,.225))
    ltext  = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    frame.set_facecolor('0.80')      # set the frame face color to light gray
    frame.set_alpha(0.5)             # set alpha low to see through
    setp(ltext, fontsize='small')    # the legend text fontsize
    setp(llines, linewidth=1.5)      # the legend linewidth
    
    #######################################
    # print ' ... Stheta'
    ax = fig.add_axes((.520,.4,.125,.45))
    axs.append(ax)
    
    xlim = (0.,0.003)
    l1, = ax.plot(Stheta, d, 'k-')
    l2 = ax.axhline(Dp, color='k', linestyle='-')
    # label ALL FREQ
    ax.text(0.5, 0.95, 'ALL FREQs', horizontalalignment='center',
            transform=ax.transAxes, bbox=dict(facecolor=None, edgecolor='k', alpha=0.5))
    ax.set_yticklabels([])
    ax.set_ylim(0., 360.)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.set_xlim(xlim)
    # ax.xaxis.set_major_locator(MaxNLocator(3))
    # ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_xticks([0.,0.001,0.002])
    ax.set_xticklabels(['0.0e-3','1.0','2.0'])
    
    #######################################
    # print ' ... Stheta_swell'
    ax = fig.add_axes((.67,.4,.125,.45))
    axs.append(ax)
    
    l1, = ax.plot(Stheta_swell, d, 'g-')
    l2 = ax.axhline(Dps, color='g', linestyle='-')
    # label SWELL 
    ax.text(0.5, 0.95, 'SWELL', color='g', horizontalalignment='center',
            transform=ax.transAxes, bbox=dict(facecolor=None, edgecolor='g', alpha=0.5))
    ax.set_yticklabels([])
    ax.set_ylim(0., 360.)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('Stheta (m2/deg)')
    ax.set_xlim(xlim)
    # ax.xaxis.set_major_locator(MaxNLocator(3))
    # ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_xticks([0.,0.001,0.002])
    ax.set_xticklabels(['0.0','1.0','2.0'])
    ax.set_title('Bogue Wave Data as of ' + last_dt_str, fontsize=14)
    # ax.set_title('Directional Spectrum')
    ax.title.set_position((-0.8, 1.25))
    
    #######################################
    # print ' ... Stheta_wind'
    ax = fig.add_axes((.82,.4,.125,.45))
    axs.append(ax)
    
    l1, = ax.plot(Stheta_wind, d, 'b-')
    l2 = ax.axhline(Dpw, color='b', linestyle='-')
    # label WIND 
    ax.text(0.5, 0.95, 'WIND', color='b', horizontalalignment='center',
            transform=ax.transAxes, bbox=dict(facecolor=None, edgecolor='b', alpha=0.5))
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.set_xlim(xlim)
    # ax.xaxis.set_major_locator(MaxNLocator(3))
    # ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_xticks([0.,0.001,0.002])
    ax.set_xticklabels(['0.0','1.0','2.0e-03'])
    
    ax.yaxis.tick_right()
    ax.set_ylim(0., 360.)
    ax.yaxis.set_label_position('right')
    ax.set_ylabel('Direction (deg N)')
    
    #######################################
    # print ' ... Hs, Hss, Hsw'
    ax = fig.add_axes((.1,.05,.8,.15))
    axs.append(ax)
    
    # use masked array to hide NaN's on plot
    Hs = numpy.ma.masked_where(numpy.isnan(Hs), Hs)
    Hss = numpy.ma.masked_where(numpy.isnan(Hss), Hss)
    Hsw = numpy.ma.masked_where(numpy.isnan(Hsw), Hsw)
    
    # ax.plot returns a list of lines, so unpack tuple
    l1, = ax.plot_date(dt, Hs, fmt='k-')
    l1.set_label('Significant Wave Height (Hs)')
    
    l2, = ax.plot_date(dt, Hss, fmt='g-')
    l2.set_label('Sig. Swell Wave Height (Hss)')
    
    l3, = ax.plot_date(dt, Hsw, fmt='b-')
    l3.set_label('Sig. Wind Wave Height (Hsw)')
    
    ax.set_ylabel('WAVE\nHEIGHT(m)')
    # ax.set_ylim(2.,10.)
    # ax.set_xlim(dt[0], dt[-1]) # first to last regardless of what
    ax.set_xlim(date2num(dt[-1])-1, date2num(dt[-1])) # last minus 30 days to last
    ax.xaxis.set_major_locator( HourLocator(range(0,25,1)) )
    ax.xaxis.set_minor_locator( MinuteLocator(range(0,61,30)) )
    ax.xaxis.set_major_formatter( DateFormatter('%H') )
    ax.set_xlabel('Bogue Wave Height -- Last 24 hours from ' + last_dt_str)
    
    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('(feet)')
    
    # legend
    ls1 = l1.get_label()
    ls2 = l2.get_label()
    ls3 = l3.get_label()
    leg = ax.legend((l1,l2,l3), (ls1,ls2,ls3), loc='upper left')
    ltext  = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    frame.set_facecolor('0.80')      # set the frame face color to light gray
    frame.set_alpha(0.5)             # set alpha low to see through
    setp(ltext, fontsize=8)          # the legend text fontsize
    setp(llines, linewidth=1.5)      # the legend linewidth
    leg.draw_frame(False)            # don't draw the legend frame
    
    # save figure
    ofn = os.path.join(odir, 'bogue_dspec_'+fn_dt_str+'.png')
    savefig(ofn)

# copy last latest
ofn2 = '/home/haines/rayleigh/img/bogue_dspec_last01days.png'
import shutil
shutil.copy(ofn, ofn2)

# copy last 24 to loop directory
import glob
gs = os.path.join(odir, '*.png')
all_pngs = glob.glob(gs)
all_pngs.sort()
j=1
for png in all_pngs[-24:]:
    ofn = '/home/haines/rayleigh/loop/bogue_dspec_plot_%d.png' % (j,)
    shutil.copy(png, ofn)
    j=j+1

#
