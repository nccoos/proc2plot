#!/usr/bin/env /opt/env/haines/dataproc/bin/python
# Last modified:  Time-stamp: <2010-08-17 15:47:11 haines>

"""bogue_adcp_plot"""

#################################################
# [1a] search and replace XXXX with platform id
# [1b] search and replace YYYY with sensor id
# [1c] search and replace ZZZZ plot titles
#################################################

# plot each month

import os
# import sys, glob, re
import datetime, time, dateutil, dateutil.tz
import pycdf
import numpy

# sys.path.append('/opt/env/haines/dataproc/raw2proc')
# del(sys)

os.environ["MPLCONFIGDIR"]="/home/haines/.matplotlib/"

from pylab import figure, twinx, savefig, setp, getp, cm, colorbar
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, DateFormatter, date2num, num2date
import procutil

def timeseries(pi, si, yyyy_mm, plot_type='latest'):
    """ 
    """


    print 'bogue_adcp_plot ...'

    #

    prev_month, this_month, next_month = procutil.find_months(yyyy_mm)
    yyyy_mm_str = this_month.strftime('%Y_%m')

    ################################
    # [2a] load primary data file
    ################################

    ncFile1='/seacoos/data/nccoos/level1/bogue/adcp/bogue_adcp_'+prev_month.strftime('%Y_%m')+'.nc'
    ncFile2='/seacoos/data/nccoos/level1/bogue/adcp/bogue_adcp_'+this_month.strftime('%Y_%m')+'.nc'

    have_ncFile1 = os.path.exists(ncFile1)
    have_ncFile2 = os.path.exists(ncFile2)

    print ' ... loading data for graph from ...'
    print ' ... ... ' + ncFile1 + ' ... ' + str(have_ncFile1)
    print ' ... ... ' + ncFile2 + ' ... ' + str(have_ncFile2)

    # open netcdf data
    if have_ncFile1 and have_ncFile2:
        nc = pycdf.CDFMF((ncFile1, ncFile2))
    elif not have_ncFile1 and have_ncFile2:
        nc = pycdf.CDFMF((ncFile2,))
    elif have_ncFile1 and not have_ncFile2:
        nc = pycdf.CDFMF((ncFile1,))
    else:
        print ' ... both files do not exist -- NO DATA LOADED'
        return

    # ncvars = nc.variables()
    # print ncvars
    es = nc.var('time')[:]
    units = nc.var('time').units
    dt = [procutil.es2dt(e) for e in es]
    # set timezone info to UTC (since data from level1 should be in UTC!!)
    dt = [e.replace(tzinfo=dateutil.tz.tzutc()) for e in dt]
    # return new datetime based on computer local
    dt_local = [e.astimezone(dateutil.tz.tzlocal()) for e in dt]
    dn = date2num(dt)

    ################################
    # [2b] specify variables 
    ################################
    z = nc.var('z')[:]
    wd = nc.var('wd')[:]
    wl = nc.var('wl')[:]
    # en = nc.var('en')[:]
    u = nc.var('u')[:]
    v = nc.var('v')[:]
    e1 = nc.var('e1')[:]

    nc.close()

    # last dt in data for labels
    dtu = dt[-1]
    dtl = dt_local[-1]

    diff = abs(dtu - dtl)
    if diff.days>0:
        last_dt_str = dtu.strftime("%H:%M %Z on %b %d, %Y") + ' (' + dtl.strftime("%H:%M %Z, %b %d") + ')'
    else:
        last_dt_str = dtu.strftime("%H:%M %Z") + ' (' + dtl.strftime("%H:%M %Z") + ')' \
                      + dtl.strftime(" on %b %d, %Y")

    #######################################
    # Plot setup
    #######################################
    # range for pcolor plots
    cmin, cmax = (-0.5, 0.5)

    fig = figure(figsize=(10, 8))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    ax = fig.add_subplot(4,1,1)
    axs = [ax]

    # replace gaps in time with NaN
    (x, y) = procutil.addnan(dt, u, maxdelta=2./24)
    dnx = date2num(x)
    # use masked array to hide NaN's on plot
    um = numpy.ma.masked_where(numpy.isnan(y), y)
    pc = ax.pcolor(dnx, z, um.T, vmin=cmin, vmax=cmax)
    pc.set_label('True Eastward Current (m s-1)')
    ax.text(0.025, 0.1, pc.get_label(), fontsize="small", transform=ax.transAxes)

    # setup colorbar axes instance
    l,b,w,h = ax.get_position().bounds
    cax = fig.add_axes([l, b+h+0.04, 0.25*w, 0.03])

    cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
    cb.set_label('Current Velocity (m s-1)')
    cb.ax.xaxis.set_label_position('top')
    cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
    cb.ax.set_xticklabels([-0.4, -0.2, 0, 0.2, 0.4])

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, wl, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='k-')
    l1.set_label('Water Level')

    ax.set_ylabel('Depth (m)')
    ax.set_ylim(-10., 2.)
    # ax.set_xlim(dt[0], dt[-1]) # first to last regardless of what  
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # this only moves the label not the tick labels
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('BOGUE Current Profile -- ' + yyyy_mm_str)

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Depth (ft)')

    ax2.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax2.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax2.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax2.set_xticklabels([])

    # legend
    ls1 = l1.get_label()
    leg = ax.legend((l1,), (ls1,), loc='upper left')
    ltext  = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    frame.set_facecolor('0.80')      # set the frame face color to light gray
    frame.set_alpha(0.5)             # set alpha low to see through
    setp(ltext, fontsize='small')    # the legend text fontsize
    setp(llines, linewidth=1.5)      # the legend linewidth
    # leg.draw_frame(False)           # don't draw the legend frame

    #######################################
    #
    ax = fig.add_subplot(4,1,2)
    axs.append(ax)

    # replace gaps in time with NaN
    (x, y) = procutil.addnan(dt, v, maxdelta=2./24)
    dnx = date2num(x)
    # use masked array to hide NaN's on plot
    vm = numpy.ma.masked_where(numpy.isnan(y), y)
    # (x, y) = procutil.addnan(dt, vm, maxdelta=2./24)
    pc = ax.pcolor(dnx, z, vm.T, vmin=cmin, vmax=cmax)
    pc.set_label('True Northward Current (m s-1)')
    ax.text(0.025, 0.1, pc.get_label(), fontsize="small", transform=ax.transAxes)

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, wl, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='k-')
    l1.set_label('Water Level')

    ax.set_ylabel('Depth (m)')
    ax.set_ylim(-10.,2.)
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Depth (ft)')

    ax2.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax2.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax2.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )

    # legend
    ls1 = l1.get_label()
    leg = ax.legend((l1,), (ls1,), loc='upper left')
    ltext  = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    frame.set_facecolor('0.80')      # set the frame face color to light gray
    frame.set_alpha(0.5)             # set alpha low to see through
    setp(ltext, fontsize='small')    # the legend text fontsize
    setp(llines, linewidth=1.5)      # the legend linewidth
    # leg.draw_frame(False)           # don't draw the legend frame

    #######################################
    #
    ax = fig.add_subplot(4,1,3)
    axs.append(ax)

    # replace gaps in time with NaN
    (x, y) = procutil.addnan(dt, e1, maxdelta=2./24)
    dnx = date2num(x)
    # use masked array to hide NaN's on plot
    vm = numpy.ma.masked_where(numpy.isnan(y), y)
    # (x, y) = procutil.addnan(dt, vm, maxdelta=2./24)
    pc = ax.pcolor(dnx, z, vm.T, vmin=0., vmax=150.)
    pc.set_label('Amplitude Beam 1 (count)')
    ax.text(0.025, 0.1, pc.get_label(), fontsize="small", transform=ax.transAxes)

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, wl, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='k-')
    l1.set_label('Water Level')

    ax.set_ylabel('Depth (m)')
    ax.set_ylim(-10.,2.)
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )

    ax.set_xlabel('BOGUE Current Profile -- ' + yyyy_mm_str)

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Depth (ft)')

    ax2.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax2.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax2.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax2.xaxis.set_major_formatter( DateFormatter('%m/%d') )

    # legend
    ls1 = l1.get_label()
    leg = ax.legend((l1,), (ls1,), loc='upper left')
    ltext  = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    frame.set_facecolor('0.80')      # set the frame face color to light gray
    frame.set_alpha(0.5)             # set alpha low to see through
    setp(ltext, fontsize='small')    # the legend text fontsize
    setp(llines, linewidth=1.5)      # the legend linewidth
    # leg.draw_frame(False)           # don't draw the legend frame


    # save figure for this month
    ofn = '/home/haines/rayleigh/img/bogue/bogue_adcp_'+yyyy_mm_str+'.png'
    print '... ... write: %s' % (ofn,)
    savefig(ofn)


    #######################################
    # Last 30 days
    #######################################
    if plot_type=='latest':
        print ' ... Last 30 days'
        for idx, ax in enumerate(axs):
            ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
            ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
            ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
            ax.set_xticklabels([])
            if idx==0:
                ax.set_xlabel('BOGUE Current Profiles -- Last 30 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BOGUE Current Profiles -- Last 30 days from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/bogue_adcp_last30days.png')


    #######################################
    # Last 7 days
    #######################################
    if plot_type=='latest':
        print ' ... Last 7 days'
        for idx, ax in enumerate(axs):
            ax.set_xlim(date2num(dt[-1])-7, date2num(dt[-1]))
            ax.xaxis.set_major_locator( DayLocator(range(0,32,1)) )
            ax.xaxis.set_minor_locator( HourLocator(range(0,25,6)) )
            ax.set_xticklabels([])
            if idx==0:
                ax.set_xlabel('BOGUE Current Profiles -- Last 7 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BOGUE Current Profiles -- Last 7 days from ' + last_dt_str)
                
        savefig('/home/haines/rayleigh/img/bogue_adcp_last07days.png')


    #######################################
    # Last 1 day (24hrs)
    #######################################
    if plot_type=='latest':
        print ' ... Last 1 days'

        for idx, ax in enumerate(axs):
            ax.set_xlim(date2num(dt[-1])-1, date2num(dt[-1]))
            ax.xaxis.set_major_locator( HourLocator(range(0,25,1)) )
            ax.xaxis.set_minor_locator( MinuteLocator(range(0,61,30)) )
            ax.set_xticklabels([])
            if idx==0:
                ax.set_xlabel('BOGUE Current Profiles -- Last 24 hours from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%H') )
                ax.set_xlabel('BOGUE Current Profiles -- Last 24 hours from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/bogue_adcp_last01days.png')

