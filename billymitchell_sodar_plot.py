#!/opt/env/haines/dataproc/bin/python
# Last modified:  Time-stamp: <2011-10-11 12:44:06 cbc>

"""billymitchell_sodar_plot"""

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
    print 'billymitchell_sodar1_plot ...'

    #

    prev_month, this_month, next_month = procutil.find_months(yyyy_mm)
    yyyy_mm_str = this_month.strftime('%Y_%m')

    ################################
    # [2a] load primary data file
    ################################

    ncFile1='/seacoos/data/nccoos/level2/billymitchell/sodar1/billymitchell_sfas_'+prev_month.strftime('%Y_%m')+'.nc'
    ncFile2='/seacoos/data/nccoos/level2/billymitchell/sodar1/billymitchell_sfas_'+this_month.strftime('%Y_%m')+'.nc'

    have_ncFile1 = os.path.exists(ncFile1)
    have_ncFile2 = os.path.exists(ncFile2)

    print ' ... loading data for graph from ...'
    print ' ... ... ' + ncFile1 + ' ... ' + str(have_ncFile1)
    print ' ... ... ' + ncFile2 + ' ... ' + str(have_ncFile2)

    # open netcdf data
    if have_ncFile1 and have_ncFile2:
        try:
            nc = pycdf.CDFMF((ncFile1, ncFile2))
        except: # files may have different dimensions
            nc = pycdf.CDFMF((ncFile2,))
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
    # set timezone info to UTC (since data from level2 should be in UTC!!)
    dt = [e.replace(tzinfo=dateutil.tz.tzutc()) for e in dt]
    # return new datetime based on computer local
    dt_local = [e.astimezone(dateutil.tz.tzlocal()) for e in dt]
    dn = date2num(dt)


    ################################
    # [2b] specify variables 
    ################################
    z = nc.var('z')[:]
    # convert cm/s to m/s
    uu = nc.var('u')[:]
    vv = nc.var('v')[:]
    ww = nc.var('w')[:]
    sigw = nc.var('sigw')[:]
    echo = nc.var('bck')[:]

    nc.close()

    # retain original dt for addnan
    dto = dt

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

    fig = figure(figsize=(10, 10))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    ax = fig.add_subplot(5,1,1)
    axs = [ax]

    # range for horizontal wind plots
    cmin, cmax = (-20., 20.)
    # print "%s : %g %g" % ('uv wind', cmin, cmax)
    # use masked array to hide NaN's on plot
    (dt, uu) = procutil.addnan(dto, uu)
    dn = date2num(dt)
    um = numpy.ma.masked_where(numpy.isnan(uu), uu)
    pc = ax.pcolor(dn, z, um.T, vmin=cmin, vmax=cmax)
    pc.set_label('True Eastward Wind (m s-1)')
    ax.text(0.025, 0.1, pc.get_label(), fontsize="small", transform=ax.transAxes)
    ax.set_ylabel('Height (m)')

    # setup colorbar axes instance.
    l,b,w,h = ax.get_position().bounds
    cax = fig.add_axes([l, b+h+0.04, 0.25*w, 0.03])

    cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
    cb.set_label('Wind Velocity (m s-1)')
    cb.ax.xaxis.set_label_position('top')
    cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
    xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=0)
    cb.ax.set_xticklabels([xtl[1], xtl[3], xtl[5], xtl[7], xtl[9]])

    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1))) 
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # this only moves the label not the tick labels
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('BILLY MITCHELL SODAR -- ' + yyyy_mm_str)

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Height (ft)')

    #######################################
    #
    ax = fig.add_subplot(5,1,2)
    axs.append(ax)

    # use masked array to hide NaN's on plot
    (dt, vv) = procutil.addnan(dto, vv)
    dn = date2num(dt)
    vm = numpy.ma.masked_where(numpy.isnan(vv), vv)
    pc = ax.pcolor(dn, z, vm.T, vmin=cmin, vmax=cmax)
    pc.set_label('True Northward Wind (m s-1)')
    ax.text(0.025, 0.1, pc.get_label(), fontsize="small", transform=ax.transAxes)
    ax.set_ylabel('Height (m)')

    # ax.set_xlim(date2num(dt[0]), date2num(dt[-1])) 
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1))) 
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
    ax.set_xticklabels([])

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Height (ft)')
    
    #######################################
    #
    ax = fig.add_subplot(5,1,3)
    axs.append(ax)
    
    # range for horizontal wind plots
    cmin, cmax = (-2., 2.)
    # print "%s : %g %g" % ('w wind', cmin, cmax)

    # use masked array to hide NaN's on plot
    (dt, ww) = procutil.addnan(dto, ww)
    dn = date2num(dt)
    wm = numpy.ma.masked_where(numpy.isnan(ww), ww)
    pc = ax.pcolor(dn, z, wm.T, vmin=cmin, vmax=cmax)
    ax.set_ylabel('Height (m)')
    
    # setup colorbar axes instance.
    l,b,w,h = ax.get_position().bounds
    cax = fig.add_axes([l+0.04, b+h-0.06, 0.25*w, 0.03])

    cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
    cb.set_label('Upward Wind Velocity (m s-1)')
    cb.ax.xaxis.set_label_position('top')
    cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
    xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=0)
    cb.ax.set_xticklabels([xtl[1], xtl[3], xtl[5], xtl[7], xtl[9]])

    # ax.set_xlim(date2num(dt[0]), date2num(dt[-1])) 
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1))) 
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
    ax.set_xticklabels([])
    
    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Height (ft)')
    
    #######################################
    #
    ax = fig.add_subplot(5,1,4)
    axs.append(ax)
    
    cmin, cmax = (0., 2.)
    # print "%s : %g %g" % ('sigw', cmin, cmax)

    # use masked array to hide NaN's on plot
    (dt, sigw) = procutil.addnan(dto, sigw)
    dn = date2num(dt)
    sm = numpy.ma.masked_where(numpy.isnan(sigw), sigw)
    pc = ax.pcolor(dn, z, sm.T, vmin=cmin, vmax=cmax)
    ax.set_ylabel('Height (m)')

    # setup colorbar axes instance.
    l,b,w,h = ax.get_position().bounds
    cax = fig.add_axes([l+0.04, b+h-0.06, 0.25*w, 0.03])

    cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
    cb.set_label('Std. Dev. of Vertical Wind (m s-1)')
    cb.ax.xaxis.set_label_position('top')
    cb.ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8])
    xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=1)
    cb.ax.set_xticklabels([xtl[0], xtl[2], xtl[4], xtl[6], xtl[8]])
    
    # ax.set_xlim(date2num(dt[0]), date2num(dt[-1])) 
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1))) 
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
    ax.set_xticklabels([])
    
    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Height (ft)')

    #######################################
    #
    ax = fig.add_subplot(5,1,5)
    axs.append(ax)

    
    # cmin, cmax = (0., 1000.)
    cmin, cmax = (2., 6.)
    # print "%s : %g %g" % ('echo', cmin, cmax)

    # use masked array to hide NaN's on plot
    (dt, echo) = procutil.addnan(dto, numpy.log10(echo))
    dn = date2num(dt)
    em = numpy.ma.masked_where(numpy.isnan(echo), echo)
    pc = ax.pcolor(dn, z, em.T, vmin=cmin, vmax=cmax)
    ax.set_ylabel('Height (m)')

    # setup colorbar axes instance.
    l,b,w,h = ax.get_position().bounds
    cax = fig.add_axes([l+0.04, b+h-0.06, 0.25*w, 0.03])

    cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
    cb.set_label('log10 Backscatter')
    cb.ax.xaxis.set_label_position('top')
    cb.ax.set_xticks([0.0, 1.0])
    xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=0)
    cb.ax.set_xticklabels([str(cmin), str(cmax)])
    
    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1))) 
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
    ax.set_xticklabels([])
    
    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Height (ft)')

    ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
    ax.set_xlabel('BILLY MITCHELL SODAR -- ' + yyyy_mm_str)
    # save figure
    
    # save figure for this month
    ofn = '/home/haines/rayleigh/img/billymitchell/billymitchell_sodar1_'+yyyy_mm_str+'.png'
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
                ax.set_xlabel('BILLY MITCHELL SODAR -- Last 30 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BILLY MITCHELL SODAR -- Last 30 days from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/billymitchell_sodar1_last30days.png')


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
                ax.set_xlabel('BILLY MITCHELL SODAR -- Last 7 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('BILLY MITCHELL SODAR -- Last 7 days from ' + last_dt_str)
                
        savefig('/home/haines/rayleigh/img/billymitchell_sodar1_last07days.png')


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
                ax.set_xlabel('BILLY MITCHELL SODAR -- Last 24 hours from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%H') )
                ax.set_xlabel('BILLY MITCHELL SODAR -- Last 24 hours from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/billymitchell_sodar1_last01days.png')


def wind_vectors(pi, si, yyyy_mm, plot_type='latest'):
    print 'billymitchell_arrows_plot ...'

    #

    prev_month, this_month, next_month = procutil.find_months(yyyy_mm)
    yyyy_mm_str = this_month.strftime('%Y_%m')

    ################################
    # [2a] load primary data file
    ################################

    ncFile1='/seacoos/data/nccoos/level2/billymitchell/sodar1/billymitchell_sfas_'+prev_month.strftime('%Y_%m')+'.nc'
    ncFile2='/seacoos/data/nccoos/level2/billymitchell/sodar1/billymitchell_sfas_'+this_month.strftime('%Y_%m')+'.nc'

    have_ncFile1 = os.path.exists(ncFile1)
    have_ncFile2 = os.path.exists(ncFile2)

    print ' ... loading data for graph from ...'
    print ' ... ... ' + ncFile1 + ' ... ' + str(have_ncFile1)
    print ' ... ... ' + ncFile2 + ' ... ' + str(have_ncFile2)

    # open netcdf data
    if have_ncFile1 and have_ncFile2:
        try:
            nc = pycdf.CDFMF((ncFile1, ncFile2))
        except: # files may have different dimensions
            nc = pycdf.CDFMF((ncFile2,))
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
    # set timezone info to UTC (since data from level2 should be in UTC!!)
    dt = [e.replace(tzinfo=dateutil.tz.tzutc()) for e in dt]
    # return new datetime based on computer local
    dt_local = [e.astimezone(dateutil.tz.tzlocal()) for e in dt]
    dn = date2num(dt)


    ################################
    # [2b] specify variables 
    ################################
    z = nc.var('z')[:]
    # convert cm/s to m/s
    uu = nc.var('u')[:]
    vv = nc.var('v')[:]
    ww = nc.var('w')[:]
    sigw = nc.var('sigw')[:]
    echo = nc.var('bck')[:]

    nc.close()

    # retain original dt for addnan
    dto = dt

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

    fig = figure(figsize=(10, 10))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    ax = fig.add_subplot(1,1,1)
    axs = [ax]

    # range for horizontal wind plots
    # cmin, cmax = (0., 20.)
    # print "%s : %g %g" % ('uv wind', cmin, cmax)
    # use masked array to hide NaN's on plot
    (dt, uu) = procutil.addnan(dto, uu)
    dn = date2num(dt)
    um = numpy.ma.masked_where(numpy.isnan(uu), uu)

    (dt, vv) = procutil.addnan(dto, vv)
    vm = numpy.ma.masked_where(numpy.isnan(vv), vv)
    wspd = numpy.sqrt(um*um + vm*vm)

    X,Y = numpy.meshgrid(dn, z)

    q1 = ax.quiver(X, Y, um.T, vm.T, wspd.T, units='inches', scale=40)
    qk = ax.quiverkey(q1, 0.1, 0.8, 20, r'20 m s-1')
    
    ax.set_ylabel('Height (m)')

    # setup colorbar axes instance.
    l,b,w,h = ax.get_position().bounds
    cax = fig.add_axes([l+0.02, b+h-0.06, 0.25*w, 0.03])

    cb = colorbar(q1, cax=cax, orientation='horizontal') # draw colorbar
    cb.set_label('Wind Velocity (m s-1)')

    # lost control of colorbar ... ???
    # 
    # cb.ax.xaxis.set_label_position('top')
    # cb.ax.set_xticks([0.0, 0.5, 1.0])
    # xtl = numpy.round(numpy.linspace(cmin, cmax, 11), decimals=0)
    # cb.ax.set_xticklabels([xtl[0], xtl[5], xtl[10]])

    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1))) 
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # this only moves the label not the tick labels
    ax.xaxis.set_label_position('bottom')
    ax.set_xlabel('BILLY MITCHELL Wind Profile -- ' + yyyy_mm_str)

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Height (ft)')

    

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
                ax.set_xlabel('BILLY MITCHELL Wind Profile -- Last 24 hours from ' + last_dt_str)
            if idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%H') )
                ax.set_xlabel('BILLY MITCHELL Wind Profile -- Last 24 hours from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/billymitchell_wind_last01days.png')


def wind_barbs(pi, si, yyyy_mm, plot_type='latest'):
    print 'billymitchell_arrows_plot ...'

    #

    prev_month, this_month, next_month = procutil.find_months(yyyy_mm)
    yyyy_mm_str = this_month.strftime('%Y_%m')

    ################################
    # [2a] load primary data file
    ################################

    ncFile1='/seacoos/data/nccoos/level2/billymitchell/sodar1/billymitchell_sfas_'+prev_month.strftime('%Y_%m')+'.nc'
    ncFile2='/seacoos/data/nccoos/level2/billymitchell/sodar1/billymitchell_sfas_'+this_month.strftime('%Y_%m')+'.nc'

    have_ncFile1 = os.path.exists(ncFile1)
    have_ncFile2 = os.path.exists(ncFile2)

    print ' ... loading data for graph from ...'
    print ' ... ... ' + ncFile1 + ' ... ' + str(have_ncFile1)
    print ' ... ... ' + ncFile2 + ' ... ' + str(have_ncFile2)

    # open netcdf data
    if have_ncFile1 and have_ncFile2:
        try:
            nc = pycdf.CDFMF((ncFile1, ncFile2))
        except: # files may have different dimensions
            nc = pycdf.CDFMF((ncFile2,))
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
    # set timezone info to UTC (since data from level2 should be in UTC!!)
    dt = [e.replace(tzinfo=dateutil.tz.tzutc()) for e in dt]
    # return new datetime based on computer local
    dt_local = [e.astimezone(dateutil.tz.tzlocal()) for e in dt]
    dn = date2num(dt)


    ################################
    # [2b] specify variables 
    ################################
    z = nc.var('z')[:]
    # convert cm/s to m/s
    uu = nc.var('u')[:]
    vv = nc.var('v')[:]
    ww = nc.var('w')[:]
    sigw = nc.var('sigw')[:]
    echo = nc.var('bck')[:]

    nc.close()

    # retain original dt for addnan
    dto = dt

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

    fig = figure(figsize=(10, 10))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

    ax = fig.add_subplot(1,1,1)
    axs = [ax]

    # range for horizontal wind plots
    # cmin, cmax = (0., 20.)
    # print "%s : %g %g" % ('uv wind', cmin, cmax)
    # use masked array to hide NaN's on plot
    (dt, uu) = procutil.addnan(dto, uu)
    dn = date2num(dt)
    um = numpy.ma.masked_where(numpy.isnan(uu), uu)

    (dt, vv) = procutil.addnan(dto, vv)
    vm = numpy.ma.masked_where(numpy.isnan(vv), vv)
    wspd = numpy.sqrt(um*um + vm*vm)

    X,Y = numpy.meshgrid(dn, z)

    q1 = ax.barbs(X, Y, um.T, vm.T, wspd.T)
    # qk = ax.quiverkey(q1, 0.1, 0.8, 20, r'20 m s-1')
    
    ax.set_ylabel('Height (m)')

    # setup colorbar axes instance.
    l,b,w,h = ax.get_position().bounds
    cax = fig.add_axes([l+0.02, b+h-0.06, 0.25*w, 0.03])

    cb = colorbar(q1, cax=cax, orientation='horizontal') # draw colorbar
    cb.set_label('Wind Velocity (m s-1)')

    # lost control of colorbar ... ???
    # 
    # cb.ax.xaxis.set_label_position('top')
    # cb.ax.set_xticks([0.0, 0.5, 1.0])
    # xtl = numpy.round(numpy.linspace(cmin, cmax, 11), decimals=0)
    # cb.ax.set_xticklabels([xtl[0], xtl[5], xtl[10]])

    ax.set_xlim(date2num(this_month), date2num(next_month-datetime.timedelta(seconds=1))) 
    ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
    ax.set_xticklabels([])

    # this only moves the label not the tick labels
    ax.xaxis.set_label_position('bottom')
    ax.set_xlabel('BILLY MITCHELL Wind Profile -- ' + yyyy_mm_str)

    # right-hand side scale
    ax2 = twinx(ax)
    ax2.yaxis.tick_right()
    # convert (lhs) meters to (rhs) feet
    feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
    ax2.set_ylim(feet)
    ax2.set_ylabel('Height (ft)')

    

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
                ax.set_xlabel('BILLY MITCHELL Wind Profile -- Last 24 hours from ' + last_dt_str)
            if idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%H') )
                ax.set_xlabel('BILLY MITCHELL Wind Profile -- Last 24 hours from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/billymitchell_windbarbs_last01days.png')

