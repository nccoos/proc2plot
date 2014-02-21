#!/usr/bin/env /opt/env/haines/dataproc/bin/python
# Last modified:  Time-stamp: <2014-02-21 10:12:36 haines>
"""plot_cr1000_gps"""

import os
import sys, glob, re
import datetime, time, dateutil, dateutil.tz
import pycdf
import numpy

sys.path.append('/opt/env/haines/dataproc/raw2proc')
# del(sys)

os.environ["MPLCONFIGDIR"]="/home/haines/.matplotlib/"

from pylab import figure, twinx, savefig, setp, getp, cm, colorbar, colors
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, DateFormatter, date2num, num2date
import procutil
import raw2proc

""" 
"""
def decdeg2dms(dd):
    mnt,sec = divmod(dd*3600,60)
    deg,mnt = divmod(mnt,60)
    return deg,mnt,sec

print 'plot_cr1000_gps ...'
img_dir = '/home/haines/rayleigh/img'

cn = 'b1_config_20131220'
pi = raw2proc.get_config(cn+'.platform_info')
asi = raw2proc.get_config(cn+'.sensor_info')
si = asi['gps']
yyyy_mm = '2014_02'
plot_type = 'latest'

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

fig = figure(figsize=(6, 5))
fig.subplots_adjust(left=0.20, bottom=0.10, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

ax = fig.add_subplot(1,1,1)
axs = [ax]

# GPS longitude on x, latitude on y
gps_lon = nc.var('gps_lon')[:]
gps_lat = nc.var('gps_lat')[:]
# gps_lon[-1:] returns last value as type numpy.array
# gps_lon[-1] returns the value as type float
(x, y) = (gps_lon[-1:], gps_lat[-1:])
# print (x, y)
# ax.plot returns a list of lines, so unpack tuple
l1, = ax.plot(x, y, 'r*', ms=8)

# anchor position platform lat and lon from config -- needs to be numpy.array([]) for ax.plot
(x, y) = (numpy.array([pi['lon']]), numpy.array([pi['lat']]))
# anchor posn platform lat and lon from netcdf file (should be the same as config)
# (x, y) = (nc.var('lon')[:], nc.var('lat')[:])
# print (x, y)
l2, = ax.plot(x, y, 'ks', ms=8, mfc='none')

# 1km watch circle, approx 111 km in 1 deg latitude 1 km is 1/111 of a deg
if 0:
    wc = Circle((x,y), 1./111, alpha=0.2)
    wc.set_label('1 km Watch Circle')
    p = PatchCollection([wc], alpha=0.2)
    ax.add_collection(p)
    leg1 = ax.legend([wc], ('1 km Watch Circle',), loc='lower left')

ax.set_xlabel('Longitude (deg)')
ax.set_ylabel('Latitude (deg)')
ax.axis('equal')

dx = numpy.diff(ax.get_xlim())
dy = numpy.diff(ax.get_ylim())

# how many degrees, how many minutes, how many seconds does this span
# (deg, mm, ss) = decdeg2dms(dx)
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
# if deg>0:
#     ax.xaxis.set_major_locator( MultipleLocator(base=1.))
#     ax.yaxis.set_major_locator( MultipleLocator(base=1.))
# elif mm>0:
#     ax.xaxis.set_major_locator( MultipleLocator(base=1./60))
#     ax.yaxis.set_major_locator( MultipleLocator(base=1./60))
# else:
#     ax.xaxis.set_major_locator( MultipleLocator(base=1./3600))
#     ax.yaxis.set_major_locator( MultipleLocator(base=1./3600))

# ax.ticklabel_format(style='plain', useOffset=ax.get_lim()[0], axis='x')
ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))
# formatter = ax.xaxis.get_major_formatter()
# formatter.set_scientific(False)
# ax.xaxis.set_major_formatter(formatter)
locator = ax.xaxis.get_major_locator()
locator._nbins=5
ax.xaxis.set_major_locator(locator)

# legend 
leg = ax.legend((l2,l1), ('Anchor Position', 'Current Buoy GPS') , loc='upper left')
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
    ax.set_title(title_str+' -- ' + yyyy_mm_str)
    dns = date2num(this_month)
    dne = date2num(next_month-datetime.timedelta(seconds=1))
    idx = (dn>=dns) & (dn<=dne)
    c = ax.scatter(gps_lon[idx],gps_lat[idx],c=dn[idx],cmap=cm.jet,vmin=dns,vmax=dne)
    cbar = fig.colorbar(c, ticks=DayLocator(range(0,32,2)),format=DateFormatter('%m/%d'))

    fn = '_'.join([pi['id'], si['id'], yyyy_mm_str+'.png'])
    ofn = os.path.join(img_dir, pi['id'], fn) # /home/haines/rayleigh/img/meet
    savefig(ofn)
    
    c.remove()
    fig.delaxes(fig.axes[1])
    fig.subplots_adjust(left=0.20, bottom=0.10, right=0.9, top=0.9, wspace=0.1, hspace=0.1)


#######################################
# Last 30 days
#######################################
if plot_type=='latest':
    print ' ... Last 30 days'
    ax.set_title(title_str+'\n Last 30 days from '+last_dt_str)
    dns = date2num(dt[-1])-30
    dne = date2num(dt[-1])
    idx = (dn>=dns) & (dn<=dne)
    c = ax.scatter(gps_lon[idx],gps_lat[idx],c=dn[idx],
                   cmap=cm.jet,vmin=dns,vmax=dne)
    cbar = fig.colorbar(c, ticks=DayLocator(range(0,32,2)),format=DateFormatter('%m/%d'))

    fn = '_'.join([pi['id'], si['id'], 'last30days.png'])
    ofn = os.path.join(img_dir, fn) # /home/haines/rayleigh/img/
    savefig(ofn)

    c.remove()
    fig.delaxes(fig.axes[1])
    fig.subplots_adjust(left=0.20, bottom=0.10, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

#######################################
# Last 7 days
#######################################
if plot_type=='latest':
    print ' ... Last 7 days'
    ax.set_title(title_str+'\n Last 7 days from '+last_dt_str)
    dns = date2num(dt[-1])-7
    dne = date2num(dt[-1])
    idx = (dn>=dns) & (dn<=dne)
    c = ax.scatter(gps_lon[idx],gps_lat[idx],c=dn[idx],
                   cmap=cm.jet,vmin=dns,vmax=dne)
    cbar = fig.colorbar(c, ticks=DayLocator(range(0,32,1)),format=DateFormatter('%m/%d'))

    fn = '_'.join([pi['id'], si['id'], 'last07days.png'])
    ofn = os.path.join(img_dir, fn) # /home/haines/rayleigh/img
    savefig(ofn)

    c.remove()
    fig.delaxes(fig.axes[1])
    fig.subplots_adjust(left=0.20, bottom=0.10, right=0.9, top=0.9, wspace=0.1, hspace=0.1)


#######################################
# Last 1 day (24hrs)
#######################################
if plot_type=='latest':
    print ' ... Last 1 days'
    ax.set_title(title_str+'\n Last 24 hours from '+last_dt_str)
    dns = date2num(dt[-1])-1
    dne = date2num(dt[-1])
    idx = (dn>=dns) & (dn<=dne)
    c = ax.scatter(gps_lon[idx],gps_lat[idx],c=dn[idx],
                   cmap=cm.jet,vmin=dns,vmax=dne)
    cbar = fig.colorbar(c, ticks=HourLocator(range(0,25,1)),format=DateFormatter('%H'))

    fn = '_'.join([pi['id'], si['id'], 'last01days.png'])
    ofn = os.path.join(img_dir, fn) # /home/haines/rayleigh/img
    savefig(ofn)

    c.remove()
    fig.delaxes(fig.axes[1])
    fig.subplots_adjust(left=0.20, bottom=0.10, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

