#!/usr/bin/env /opt/env/haines/dataproc/bin/python
# Last modified:  Time-stamp: <2014-02-21 15:59:59 haines>
"""plot_cr1000_sys"""

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
    print 'plot_cr1000_sys ...'
    img_dir = '/home/haines/rayleigh/img'

    prev_month, this_month, next_month = procutil.find_months(yyyy_mm)
    yyyy_mm_str = this_month.strftime('%Y_%m')

    fn = '_'.join([pi['id'], si['id'], prev_month.strftime('%Y_%m')+'.nc'])
    ncFile1= os.path.join(si['proc_dir'], fn)
    fn = '_'.join([pi['id'], si['id'], this_month.strftime('%Y_%m')+'.nc'])
    ncFile2= os.path.join(si['proc_dir'], fn)

    # ncFile1='/seacoos/data/nccoos/level1/meet/wq/meet_wq_'+prev_month.strftime('%Y_%m')+'.nc'
    # ncFile2='/seacoos/data/nccoos/level1/meet/wq/meet_wq_'+this_month.strftime('%Y_%m')+'.nc'

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
    # Build Plot 
    #######################################

    fig = figure(figsize=(10, 9))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    ax = fig.add_subplot(4,1,1)
    axs = [ax]

    vn = 'batt_min'
    (x, y) = procutil.addnan(dt, nc.var(vn)[:])
    # ibad = y <= -6999.
    # y[ibad] = numpy.nan

    # ax.plot returns a list of lines, so unpack tuple
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label('Battery Min')

    vn = 'batt_max'
    (x, y) = procutil.addnan(dt, nc.var(vn)[:])
    # ibad = y <= -6999.
    # y[ibad] = numpy.nan

    # ax.plot returns a list of lines, so unpack tuple
    l2, = ax.plot_date(x, y, fmt='k-', alpha=0.5)
    l2.set_label('Battery Max')
    
    ax.set_ylabel('Battery\n ('+nc.var(vn).units+')')

    # this only moves the label not the tick labels
    ax.xaxis.set_label_position('top')

    # legend
    leg = ax.legend((l1,l2), (l1.get_label(), l2.get_label()), loc='upper left')
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

    vn = 'can_temp'
    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, nc.var(vn)[:])
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label(nc.var(vn).long_name)

    ax.set_ylabel('Temp \n ('+nc.var(vn).units+')')
    # ax.set_ylim(0,10)

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) deg C to (rhs) deg F
    f = [procutil.udconvert(val, 'degreeC', 'degreeF')[0] for val in ax.get_ylim()]    
    ax2.set_ylim(f)
    ax2.set_ylabel('(deg F)')

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

    vn = 'can_rh'
    # ax.plot returns a list of lines, so unpack tuple
    (x, y) = procutil.addnan(dt, nc.var(vn)[:])
    l1, = ax.plot_date(x, y, fmt='b-')
    l1.set_label(nc.var(vn).long_name)

    ax.set_ylabel('RHUM '+nc.var(vn).units+')')
    # ax.set_ylim(20,120)

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
    # YYYY_MM 
    #######################################
    title_str = ' '.join([pi['id'].upper(), si['description']])
    
    if plot_type=='latest' or plot_type=='monthly':
        print ' ... : %s' % (yyyy_mm_str,)
        # save figure for this month
        for idx, ax in enumerate(axs):
            ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1)))
            ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
            ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
            ax.set_xticklabels([])
            if idx==0:
                ax.set_xlabel(title_str+' -- ' + yyyy_mm_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel(title_str+' -- ' + yyyy_mm_str)

        fn = '_'.join([pi['id'], si['id'], yyyy_mm_str+'.png'])
        ofn = os.path.join(img_dir, pi['id'], fn) # /home/haines/rayleigh/img/meet
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
                ax.set_xlabel(title_str+' -- Last 30 days from '+last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel(title_str+' -- Last 30 days from '+last_dt_str)

        fn = '_'.join([pi['id'], si['id'], 'last30days.png'])
        ofn = os.path.join(img_dir, fn) # /home/haines/rayleigh/img/
        savefig(ofn)

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
                ax.set_xlabel(title_str+' -- Last 7 days from '+last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel(title_str+' -- Last 7 days from '+last_dt_str)
                
        fn = '_'.join([pi['id'], si['id'], 'last07days.png'])
        ofn = os.path.join(img_dir, fn) # /home/haines/rayleigh/img
        savefig(ofn)

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
                ax.set_xlabel(title_str+' -- Last 24 hours from '+last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%H') )
                ax.set_xlabel(title_str+' -- Last 24 hours from '+last_dt_str)


        fn = '_'.join([pi['id'], si['id'], 'last01days.png'])
        ofn = os.path.join(img_dir, fn) # /home/haines/rayleigh/img
        savefig(ofn)




