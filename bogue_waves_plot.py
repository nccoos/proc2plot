#!/usr/bin/env /opt/env/haines/dataproc/bin/python
# Last modified:  Time-stamp: <2010-08-13 15:56:06 haines>

"""
bogue_adcpwaves_plot

allwaves()
swellwaves()
windwaves()
"""

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

def swellwaves(pi, si, yyyy_mm, plot_type='latest'):
    """ 
    """

    print 'bogue_swellwaves_plot ...'

    #

    prev_month, this_month, next_month = procutil.find_months(yyyy_mm)
    yyyy_mm_str = this_month.strftime('%Y_%m')

    ################################
    # [2a] load primary data file
    ################################

    ncFile1='/seacoos/data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_'+prev_month.strftime('%Y_%m')+'.nc'
    ncFile2='/seacoos/data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_'+this_month.strftime('%Y_%m')+'.nc'

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
    Hss = nc.var('Hs_swell')[:]
    Tps = nc.var('Tp_swell')[:]
    Tms = nc.var('Tm_swell')[:]
    # Hmax = nc.var('Hmax')[:]
    Dps = nc.var('Dp_swell')[:]
    Dms = nc.var('Dm_swell')[:]

    nc.close()


    ################################
    # [3a] load ancillary files if needed
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
    es2 = nc.var('time')[:]
    units = nc.var('time').units
    dt2 = [procutil.es2dt(e) for e in es2]
    # set timezone info to UTC (since data from level1 should be in UTC!!)
    dt2 = [e.replace(tzinfo=dateutil.tz.tzutc()) for e in dt2]
    dn2 = date2num(dt2)

    ################################
    # [3b] specify variables
    ################################
    wd2 = nc.var('wd')[:]

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

    fig = figure(figsize=(10, 8))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    ax = fig.add_subplot(4,1,1)
    axs = [ax]

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt2, wd2, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Water Depth (m)')

    ax.set_ylabel('Depth (m)')
    # ax.set_ylim(2.,10.)
    # ax.set_xlim(dt[0], dt[-1]) # first to last regardless of what  
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # this only moves the label not the tick labels
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('BOGUE Swell Waves -- ' + yyyy_mm_str)

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Depth (feet)')

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

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, Hss, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Significant Swell Wave Height (Hss)')

    # (x, y) = procutil.addnan(dt, Hmax, maxdelta=2./24)
    # l2, = ax.plot_date(x, y, fmt='g-')
    # l2.set_label('Max Wave Height (Hmax)')

    ax.set_ylabel('WAVE\nHEIGHT (m)')
    # ax.set_ylim(2.,10.)
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('(feet)')

    ax2.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax2.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax2.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax2.set_xticklabels([])

    # legend
    ls1 = l1.get_label()
    # ls2 = l2.get_label()
    # leg = ax.legend((l1,l2), (ls1,ls2), loc='upper left')
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

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, Tps, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Peak Swell Period (Tp)')

    (x, y) = procutil.addnan(dt, Tms, maxdelta=2./24)
    l2, = ax.plot_date(x, y, fmt='c-')
    l2.set_label('Mean Swell Period (Tm)')

    ax.set_ylabel('WAVE\nPERIOD (s)')
    # ax.set_ylim(2.,10.)
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # legend
    ls1 = l1.get_label()
    ls2 = l2.get_label()
    leg = ax.legend((l1,l2), (ls1,ls2), loc='upper left')
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
    ax = fig.add_subplot(4,1,4)
    axs.append(ax)

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, Dps, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Peak Swell Direction (Dp)')

    (x, y) = procutil.addnan(dt, Dms, maxdelta=2./24) 
    l2, = ax.plot_date(x, y, fmt='c-')
    l2.set_label('Mean Swell Direction (Dp)')

    ax.set_ylabel('WAVE\nDIR (deg N)')
    ax.set_ylim(0.,360.)
    # first to last regardless of what
    # ax.set_xlim(dt[0], dt[-1])
    # last minus 30 days, 
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )

    ax.set_xlabel('BOGUE Swell Waves -- ' + yyyy_mm_str)

    # legend
    ls1 = l1.get_label()
    ls2 = l2.get_label()
    leg = ax.legend((l1,l2), (ls1,ls2), loc='upper left')
    ltext  = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    frame.set_facecolor('0.80')      # set the frame face color to light gray
    frame.set_alpha(0.5)             # set alpha low to see through
    setp(ltext, fontsize='small')    # the legend text fontsize
    setp(llines, linewidth=1.5)      # the legend linewidth
    # leg.draw_frame(False)           # don't draw the legend frame

    # save figure for this month
    ofn = '/home/haines/rayleigh/img/bogue/bogue_swellwaves_'+yyyy_mm_str+'.png'
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
                ax.set_xlabel('BOGUE Swell Waves -- Last 30 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BOGUE Swell Waves -- Last 30 days from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/bogue_swellwaves_last30days.png')


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
                ax.set_xlabel('BOGUE Swell Waves -- Last 7 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BOGUE Swell Waves -- Last 7 days from ' + last_dt_str)
                
        savefig('/home/haines/rayleigh/img/bogue_swellwaves_last07days.png')


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
                ax.set_xlabel('BOGUE Swell Waves -- Last 24 hours from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%H') )
                ax.set_xlabel('BOGUE Swell Waves -- Last 24 hours from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/bogue_swellwaves_last01days.png')


def windwaves(pi, si, yyyy_mm, plot_type='latest'):
    """ 
    """

    print 'bogue_windwaves_plot ...'

    #

    prev_month, this_month, next_month = procutil.find_months(yyyy_mm)
    yyyy_mm_str = this_month.strftime('%Y_%m')

    ################################
    # [2a] load primary data file
    ################################

    ncFile1='/seacoos/data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_'+prev_month.strftime('%Y_%m')+'.nc'
    ncFile2='/seacoos/data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_'+this_month.strftime('%Y_%m')+'.nc'

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
    Hsw = nc.var('Hs_wind')[:]
    Tpw = nc.var('Tp_wind')[:]
    Tmw = nc.var('Tm_wind')[:]
    # Hmax = nc.var('Hmax')[:]
    Dpw = nc.var('Dp_wind')[:]
    Dmw = nc.var('Dm_wind')[:]

    nc.close()

    ################################
    # [3a] load ancillary files if needed
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
    es2 = nc.var('time')[:]
    units = nc.var('time').units
    dt2 = [procutil.es2dt(e) for e in es2]
    # set timezone info to UTC (since data from level1 should be in UTC!!)
    dt2 = [e.replace(tzinfo=dateutil.tz.tzutc()) for e in dt2]
    dn2 = date2num(dt2)

    ################################
    # [3b] specify variables
    ################################
    wd2 = nc.var('wd')[:]

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

    fig = figure(figsize=(10, 8))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    ax = fig.add_subplot(4,1,1)
    axs = [ax]

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt2, wd2, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Water Depth (m)')

    ax.set_ylabel('Depth (m)')
    # ax.set_ylim(2.,10.)
    # ax.set_xlim(dt[0], dt[-1]) # first to last regardless of what  
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # this only moves the label not the tick labels
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('BOGUE Wind Waves -- ' + yyyy_mm_str)

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Depth (feet)')

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

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, Hsw, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Significant Wind Wave Height (Hss)')

    # (x, y) = procutil.addnan(dt, Hmax, maxdelta=2./24)
    # l2, = ax.plot_date(x, y, fmt='g-')
    # l2.set_label('Max Wave Height (Hmax)')

    ax.set_ylabel('WAVE\nHEIGHT (m)')
    # ax.set_ylim(2.,10.)
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('(feet)')

    ax2.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax2.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax2.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax2.set_xticklabels([])

    # legend
    ls1 = l1.get_label()
    # ls2 = l2.get_label()
    # leg = ax.legend((l1,l2), (ls1,ls2), loc='upper left')
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

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, Tpw, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Peak Wind Period (Tp)')

    (x, y) = procutil.addnan(dt, Tmw, maxdelta=2./24)
    l2, = ax.plot_date(x, y, fmt='c-')
    l2.set_label('Mean Wind Period (Tm)')

    ax.set_ylabel('WAVE\nPERIOD (s)')
    # ax.set_ylim(2.,10.)
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # legend
    ls1 = l1.get_label()
    ls2 = l2.get_label()
    leg = ax.legend((l1,l2), (ls1,ls2), loc='upper left')
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
    ax = fig.add_subplot(4,1,4)
    axs.append(ax)

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, Dpw, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Peak Wind Direction (Dp)')

    (x, y) = procutil.addnan(dt, Dmw, maxdelta=2./24) 
    l2, = ax.plot_date(x, y, fmt='c-')
    l2.set_label('Mean Wind Direction (Dp)')

    ax.set_ylabel('WAVE\nDIR (deg N)')
    ax.set_ylim(0.,360.)
    # first to last regardless of what
    # ax.set_xlim(dt[0], dt[-1])
    # last minus 30 days, 
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )

    ax.set_xlabel('BOGUE Wind Waves -- ' + yyyy_mm_str)

    # legend
    ls1 = l1.get_label()
    ls2 = l2.get_label()
    leg = ax.legend((l1,l2), (ls1,ls2), loc='upper left')
    ltext  = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    frame.set_facecolor('0.80')      # set the frame face color to light gray
    frame.set_alpha(0.5)             # set alpha low to see through
    setp(ltext, fontsize='small')    # the legend text fontsize
    setp(llines, linewidth=1.5)      # the legend linewidth
    # leg.draw_frame(False)           # don't draw the legend frame

    # save figure for this month
    ofn = '/home/haines/rayleigh/img/bogue/bogue_windwaves_'+yyyy_mm_str+'.png'
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
                ax.set_xlabel('BOGUE Wind Waves -- Last 30 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BOGUE Wind Waves -- Last 30 days from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/bogue_windwaves_last30days.png')


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
                ax.set_xlabel('BOGUE Wind Waves -- Last 7 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BOGUE Wind Waves -- Last 7 days from ' + last_dt_str)
                
        savefig('/home/haines/rayleigh/img/bogue_windwaves_last07days.png')


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
                ax.set_xlabel('BOGUE Wind Waves -- Last 24 hours from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%H') )
                ax.set_xlabel('BOGUE Wind Waves -- Last 24 hours from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/bogue_windwaves_last01days.png')




def allwaves(pi, si, yyyy_mm, plot_type='latest'):
    print 'bogue_allwaves_plot ...'

    prev_month, this_month, next_month = procutil.find_months(yyyy_mm)
    yyyy_mm_str = this_month.strftime('%Y_%m')

    ################################
    # [2a] load primary data file
    ################################

    ncFile1='/seacoos/data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_'+prev_month.strftime('%Y_%m')+'.nc'
    ncFile2='/seacoos/data/nccoos/level1/bogue/adcpwaves/bogue_adcpwaves_'+this_month.strftime('%Y_%m')+'.nc'

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
    Hs = nc.var('Hs')[:]
    Tp = nc.var('Tp')[:]
    Tm = nc.var('Tm')[:]
    # Hmax = nc.var('Hmax')[:]
    Dp = nc.var('Dp')[:]
    Dm = nc.var('Dm')[:]

    nc.close()

    ################################
    # [3a] load ancillary files if needed
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
    es2 = nc.var('time')[:]
    units = nc.var('time').units
    dt2 = [procutil.es2dt(e) for e in es2]
    # set timezone info to UTC (since data from level1 should be in UTC!!)
    dt2 = [e.replace(tzinfo=dateutil.tz.tzutc()) for e in dt2]
    dn2 = date2num(dt2)

    ################################
    # [3b] specify variables
    ################################
    wd2 = nc.var('wd')[:]

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

    fig = figure(figsize=(10, 8))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    ax = fig.add_subplot(4,1,1)
    axs = [ax]

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt2, wd2, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Water Depth (m)')

    ax.set_ylabel('Depth (m)')
    # ax.set_ylim(2.,10.)
    # ax.set_xlim(dt[0], dt[-1]) # first to last regardless of what  
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # this only moves the label not the tick labels
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('BOGUE Wind Waves -- ' + yyyy_mm_str)

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Depth (feet)')

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

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, Hs, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Significant Wave Height (Hs)')

    # (x, y) = procutil.addnan(dt, Hmax, maxdelta=2./24)
    # l2, = ax.plot_date(x, y, fmt='g-')
    # l2.set_label('Max Wave Height (Hmax)')

    ax.set_ylabel('WAVE\nHEIGHT (m)')
    # ax.set_ylim(2.,10.)
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('(feet)')

    ax2.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax2.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax2.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax2.set_xticklabels([])

    # legend
    ls1 = l1.get_label()
    # ls2 = l2.get_label()
    # leg = ax.legend((l1,l2), (ls1,ls2), loc='upper left')
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

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, Tp, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Peak Period (Tp)')

    (x, y) = procutil.addnan(dt, Tm, maxdelta=2./24)
    l2, = ax.plot_date(x, y, fmt='c-')
    l2.set_label('Mean Period (Tm)')

    ax.set_ylabel('WAVE\nPERIOD (s)')
    # ax.set_ylim(2.,10.)
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # legend
    ls1 = l1.get_label()
    ls2 = l2.get_label()
    leg = ax.legend((l1,l2), (ls1,ls2), loc='upper left')
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
    ax = fig.add_subplot(4,1,4)
    axs.append(ax)

    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, Dp, maxdelta=2./24)
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Peak Direction (Dp)')

    (x, y) = procutil.addnan(dt, Dm, maxdelta=2./24) 
    l2, = ax.plot_date(x, y, fmt='c-')
    l2.set_label('Mean Direction (Dp)')

    ax.set_ylabel('WAVE\nDIR (deg N)')
    ax.set_ylim(0.,360.)
    # first to last regardless of what
    # ax.set_xlim(dt[0], dt[-1])
    # last minus 30 days, 
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )

    ax.set_xlabel('BOGUE Waves -- ' + yyyy_mm_str)

    # legend
    ls1 = l1.get_label()
    ls2 = l2.get_label()
    leg = ax.legend((l1,l2), (ls1,ls2), loc='upper left')
    ltext  = leg.get_texts()  # all the text.Text instance in the legend
    llines = leg.get_lines()  # all the lines.Line2D instance in the legend
    frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
    frame.set_facecolor('0.80')      # set the frame face color to light gray
    frame.set_alpha(0.5)             # set alpha low to see through
    setp(ltext, fontsize='small')    # the legend text fontsize
    setp(llines, linewidth=1.5)      # the legend linewidth
    # leg.draw_frame(False)           # don't draw the legend frame

    # save figure for this month
    ofn = '/home/haines/rayleigh/img/bogue/bogue_allwaves_'+yyyy_mm_str+'.png'
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
                ax.set_xlabel('BOGUE All Waves -- Last 30 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BOGUE All Waves -- Last 30 days from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/bogue_allwaves_last30days.png')


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
                ax.set_xlabel('BOGUE All Waves -- Last 7 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BOGUE All Waves -- Last 7 days from ' + last_dt_str)
                
        savefig('/home/haines/rayleigh/img/bogue_allwaves_last07days.png')


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
                ax.set_xlabel('BOGUE All Waves -- Last 24 hours from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%H') )
                ax.set_xlabel('BOGUE All Waves -- Last 24 hours from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/bogue_allwaves_last01days.png')




