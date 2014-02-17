#!/usr/bin/env /opt/env/haines/dataproc/bin/python
# Last modified:  Time-stamp: <2010-04-07 12:02:53 haines>

"""XXXX_YYYY_plot"""

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


    print 'XXXX_YYYY_plot ...'

    #

    prev_month, this_month, next_month = procutil.find_months(yyyy_mm)
    yyyy_mm_str = this_month.strftime('%Y_%m')

    ################################
    # [2a] load primary data file
    ################################

    ncFile1='/seacoos/data/nccoos/level1/XXXX/YYYY/XXXX_YYYY_'+prev_month.strftime('%Y_%m')+'.nc'
    ncFile2='/seacoos/data/nccoos/level1/XXXX/YYYY/XXXX_YYYY_'+this_month.strftime('%Y_%m')+'.nc'

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

    # e.g.
    # z = nc.var('z')[:]

    nc.close()


    ################################
    # [3a] load ancillary files if needed
    ################################

    ncFile1='/seacoos/data/nccoos/level1/XXXX/flow/XXXX_flow_'+prev_month.strftime('%Y_%m')+'.nc'
    ncFile2='/seacoos/data/nccoos/level1/XXXX/flow/XXXX_flow_'+this_month.strftime('%Y_%m')+'.nc'

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


    # save figure for this month
    ofn = '/home/haines/rayleigh/img/XXXX/XXXX_YYYY_'+yyyy_mm_str+'.png'
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
                ax.set_xlabel('XXXX ZZZZ -- Last 30 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('XXXX ZZZZ -- Last 30 days from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/XXXX_YYYY_last30days.png')


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
                ax.set_xlabel('XXXX ZZZZ -- Last 7 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('XXXX ZZZZ -- Last 7 days from ' + last_dt_str)
                
        savefig('/home/haines/rayleigh/img/XXXX_YYYY_last07days.png')


    #######################################
    # Last 1 day (24hrs)
    #######################################
    if plot_type=='latest':
        print ' ... Last 1 days'

        for idx, ax in enumerate(axs):
            ax.set_xlim(date2num(dt[-1])-1, date2num(dt[-1]))
            ax.xaxis.set_major_locator( DayLocator(range(0,32,1)) )
            ax.xaxis.set_minor_locator( HourLocator(range(0,25,6)) )
            ax.set_xticklabels([])
            if idx==0:
                ax.set_xlabel('XXXX ZZZZ -- Last 24 hours from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('XXXX ZZZZ -- Last 24 hours from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/XXXX_YYYY_last01days.png')




