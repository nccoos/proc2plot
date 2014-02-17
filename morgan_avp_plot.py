#!/usr/bin/env python
# Last modified:  Time-stamp: <2011-02-25 17:02:13 haines>
"""morgan_avp_plot"""

import os, sys
import datetime, time, dateutil, dateutil.tz
import pycdf
import numpy

sys.path.append('/home/haines/dataproc/raw2proc')
del(sys)

os.environ["MPLCONFIGDIR"]="/home/haines/.matplotlib/"

from pylab import figure, twinx, savefig, setp, getp, cm, colorbar
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, DateFormatter, date2num, num2date
import procutil

print 'morgan_avp_plot ...'
prev_month, this_month, next_month = procutil.find_months(procutil.this_month())
ncFile1='/seacoos/data/nccoos/level1/morgan/avp/morgan_avp_2012_01.nc'
ncFile2='/seacoos/data/nccoos/level1/morgan/avp/morgan_avp_2012_02.nc'
# ncFile1='/seacoos/data/nccoos/level1/morgan/avp/morgan_avp_'+prev_month.strftime('%Y_%m')+'.nc'
# ncFile2='/seacoos/data/nccoos/level1/morgan/avp/morgan_avp_'+this_month.strftime('%Y_%m')+'.nc'

have_ncFile1 = os.path.exists(ncFile1)
have_ncFile2 = os.path.exists(ncFile2)

print ' ... loading data for graph from ...'
print ' ... ... ' + ncFile1 + ' ... ' + str(have_ncFile1)
print ' ... ... ' + ncFile2 + ' ... ' + str(have_ncFile2)

if have_ncFile1 and have_ncFile2:
    nc = pycdf.CDFMF((ncFile1, ncFile2))
elif not have_ncFile1 and have_ncFile2:
    nc = pycdf.CDFMF((ncFile2,))
elif have_ncFile1 and not have_ncFile2:
    nc = pycdf.CDFMF((ncFile1,))
else:
    print ' ... both files do not exist -- NO DATA LOADED'
    return

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
z = nc.var('z')[:]
wd = nc.var('wd')[:]
wtemp = nc.var('wtemp')[:]
salin = nc.var('salin')[:]
turb = nc.var('turb')[:]
ph = nc.var('ph')[:]
do = nc.var('do')[:]
chl = nc.var('chl')[:]
nc.close()

# last dt in data for labels
dt1 = dt[-1]
dt2 = dt_local[-1]

diff = abs(dt1 - dt2)
if diff.days>0:
    last_dt_str = dt1.strftime("%H:%M %Z on %b %d, %Y") + ' (' + dt2.strftime("%H:%M %Z, %b %d") + ')'
else:
    last_dt_str = dt1.strftime("%H:%M %Z") + ' (' + dt2.strftime("%H:%M %Z") + ')' \
              + dt2.strftime(" on %b %d, %Y")
# add a couple of inches to length of page for 6 subplots (5 subs in 8 inches, 6 subs in 10)
fig = figure(figsize=(10, 10))
fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)



#######################################
# Last 30 days
#######################################
print ' ... Last 30 days'
ax = fig.add_subplot(6,1,1)
axs = [ax]

# use masked array to hide NaN's on plot
wtm = numpy.ma.masked_where(numpy.isnan(wtemp), wtemp)
# range for pcolor plots
cmin = numpy.floor(wtm.min())
cmax = cmin+8.
# print "%s : %g %g" % ('Temp', cmin, cmax)
# cmin, cmax = (15., 35.)
# plot pcolor
pc = ax.pcolor(dn, z, wtm.T, cmap=cm.get_cmap('jet'), vmin=cmin, vmax=cmax)

# setup colorbar axes instance.
l,b,w,h = ax.get_position()
cax = fig.add_axes([l+0.04, b+0.02, 0.25*w, 0.03])

cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
cb.set_label('Water Temperature (deg C)')
cb.ax.xaxis.set_label_position('top')
cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
# make tick labels for 10 posns set and round to one decimal place
xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=1)
# but only select one at set_xticks
cb.ax.set_xticklabels([xtl[1], xtl[3], xtl[5], xtl[7], xtl[9]])

# ax.plot returns a list of lines, so unpack tuple
# l1, = ax.plot_date(dt, wd, fmt='k-')
# l1.set_label('Water Level')

ax.set_ylabel('Depth (m)')
ax.set_ylim(-4.,0.)
# ax.set_xlim(dt[0], dt[-1]) # first to last regardless of what  
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1])) # last minus 30 days to last
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.set_xticklabels([])

# this only moves the label not the tick labels
ax.xaxis.set_label_position('top')
ax.set_xlabel('Morgan Bay AVP -- Last 30 days from ' + last_dt_str)

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) meters to (rhs) feet
feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
ax2.set_ylim(feet)
ax2.set_ylabel('Depth (ft)')

# legend
# ls1 = l1.get_label()
# leg = ax.legend((l1,), (ls1,), loc='upper left')
# ltext  = leg.get_texts()  # all the text.Text instance in the legend
# llines = leg.get_lines()  # all the lines.Line2D instance in the legend
# frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
# frame.set_facecolor('0.80')      # set the frame face color to light gray
# frame.set_alpha(0.5)             # set alpha low to see through
# setp(ltext, fontsize='small')    # the legend text fontsize
# setp(llines, linewidth=1.5)      # the legend linewidth
# leg.draw_frame(False)           # don't draw the legend frame

#######################################
#
ax = fig.add_subplot(6,1,2)
axs.append(ax)

# use masked array to hide NaN's on plot
sm = numpy.ma.masked_where(numpy.isnan(salin), salin)
# range for pcolor plots
cmin = numpy.floor(sm.mean()-2*sm.std())
cmax = cmin+10.
# print "%s : %g %g" % ('Salin', cmin, cmax)
# cmin, cmax = (0., 50.)
pc = ax.pcolor(dn, z, sm.T, cmap=cm.get_cmap('Blues_r'), vmin=cmin, vmax=cmax)

# setup colorbar axes instance.
l,b,w,h = ax.get_position()
cax = fig.add_axes([l+0.04, b+0.02, 0.25*w, 0.03])

cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
cb.set_label('Salinity (PSU)')
cb.ax.xaxis.set_label_position('top')
cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=1)
cb.ax.set_xticklabels([xtl[1], xtl[3], xtl[5], xtl[7], xtl[9]])

# ax.plot returns a list of lines, so unpack tuple
# l1, = ax.plot_date(dt, wd, fmt='k-')
# l1.set_label('Water Level')

ax.set_ylabel('Depth (m)')
ax.set_ylim(-4.,0.)
# first to last regardless of what
# ax.set_xlim(dt[0], dt[-1])
# last minus 30 days, 
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.set_xticklabels([])

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) meters to (rhs) feet
feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
ax2.set_ylim(feet)
ax2.set_ylabel('Depth (ft)')

# legend
# ls1 = l1.get_label()
# leg = ax.legend((l1,), (ls1,), loc='upper left')
# ltext  = leg.get_texts()  # all the text.Text instance in the legend
# llines = leg.get_lines()  # all the lines.Line2D instance in the legend
# frame  = leg.get_frame()  # the patch.Rectangle instance surrounding the legend
# frame.set_facecolor('0.80')      # set the frame face color to light gray
# frame.set_alpha(0.5)             # set alpha low to see through
# setp(ltext, fontsize='small')    # the legend text fontsize
# setp(llines, linewidth=1.5)      # the legend linewidth
# leg.draw_frame(False)           # don't draw the legend frame

#######################################
#
ax = fig.add_subplot(6,1,3)
axs.append(ax)

# use masked array to hide NaN's on plot
sm = numpy.ma.masked_where(numpy.isnan(turb), turb)
# range for pcolor plots
# cmin, cmax = numpy.round([sm.min(), sm.max()], decimals=0)
# cmin = cmin-1
# cmax = cmax+1
cmin, cmax = (0., 10.)
# print "%s : %g %g" % ('Turb', cmin, cmax)
pc = ax.pcolor(dn, z, sm.T, cmap=cm.get_cmap('YlOrBr'), vmin=cmin, vmax=cmax)

# setup colorbar axes instance.
l,b,w,h = ax.get_position()
cax = fig.add_axes([l+0.04, b+0.02, 0.25*w, 0.03])

cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
cb.set_label('Turbidity (NTU)')
cb.ax.xaxis.set_label_position('top')
cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=0)
cb.ax.set_xticklabels([xtl[1], xtl[3], xtl[5], xtl[7], xtl[9]])
# cb.ax.set_xticklabels([12., 16., 20., 24., 28.])

# ax.plot returns a list of lines, so unpack tuple
# l1, = ax.plot_date(dt, wd, fmt='k-')
# l1.set_label('Water Level')

ax.set_ylabel('Depth (m)')
ax.set_ylim(-4.,0.)
# first to last regardless of what
# ax.set_xlim(dt[0], dt[-1])
# last minus 30 days, 
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.set_xticklabels([])

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) meters to (rhs) feet
feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
ax2.set_ylim(feet)
ax2.set_ylabel('Depth (ft)')

#######################################
#
ax = fig.add_subplot(6,1,4)
axs.append(ax)

# use masked array to hide NaN's on plot
sm = numpy.ma.masked_where(numpy.isnan(chl), chl)
# range for pcolor plots
cmin = numpy.floor(sm.min())
cmax = cmin+15.
# print "%s : %g %g" % ('Chloro', cmin, cmax)
# cmin, cmax = (0., 100.)
pc = ax.pcolor(dn, z, sm.T, cmap=cm.get_cmap('BuGn'), vmin=cmin, vmax=cmax)

# setup colorbar axes instance.
l,b,w,h = ax.get_position()
cax = fig.add_axes([l+0.04, b+0.02, 0.25*w, 0.03])

cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
cb.set_label('Chlorophyll (ug l-1)')
cb.ax.xaxis.set_label_position('top')
cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=1)
cb.ax.set_xticklabels([xtl[1], xtl[3], xtl[5], xtl[7], xtl[9]])
# cb.ax.set_xticklabels([12., 16., 20., 24., 28.])

# ax.plot returns a list of lines, so unpack tuple
# l1, = ax.plot_date(dt, wd, fmt='k-')
# l1.set_label('Water Level')

ax.set_ylabel('Depth (m)')
ax.set_ylim(-4.,0.)
# first to last regardless of what
# ax.set_xlim(dt[0], dt[-1])
# last minus 30 days, 
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.set_xticklabels([])

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) meters to (rhs) feet
feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
ax2.set_ylim(feet)
ax2.set_ylabel('Depth (ft)')

#######################################
#
ax = fig.add_subplot(6,1,5)
axs.append(ax)

# use masked array to hide NaN's on plot
sm = numpy.ma.masked_where(numpy.isnan(do), do)
# range for pcolor plots
cmin, cmax = (0., 15.)
pc = ax.pcolor(dn, z, sm.T, cmap=cm.get_cmap('PiYG'), vmin=cmin, vmax=cmax)

# setup colorbar axes instance.
l,b,w,h = ax.get_position()
cax = fig.add_axes([l+0.04, b+0.02, 0.25*w, 0.03])

cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
cb.set_label('Dissolved Oxygen (mg l-1)')
cb.ax.xaxis.set_label_position('top')
cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=0)
cb.ax.set_xticklabels([xtl[1], xtl[3], xtl[5], xtl[7], xtl[9]])
# cb.ax.set_xticklabels([12., 16., 20., 24., 28.])

# ax.plot returns a list of lines, so unpack tuple
# l1, = ax.plot_date(dt, wd, fmt='k-')
# l1.set_label('Water Level')

ax.set_ylabel('Depth (m)')
ax.set_ylim(-4.,0.)
# first to last regardless of what
# ax.set_xlim(dt[0], dt[-1])
# last minus 30 days, 
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.set_xticklabels([])

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) meters to (rhs) feet
feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
ax2.set_ylim(feet)
ax2.set_ylabel('Depth (ft)')

#######################################
#
ax = fig.add_subplot(6,1,6)
axs.append(ax)

# use masked array to hide NaN's on plot
sm = numpy.ma.masked_where(numpy.isnan(ph), ph)
# range for pcolor plots
# cmin, cmax = numpy.round([sm.min(), sm.max()], decimals=0)
# cmin = cmin-1
# cmax = cmax+1
cmin, cmax = (6., 8.)
print "%s : %g %g" % ('pH', cmin, cmax)
pc = ax.pcolor(dn, z, sm.T, cmap=cm.get_cmap('cool'), vmin=cmin, vmax=cmax)

# setup colorbar axes instance.
l,b,w,h = ax.get_position()
cax = fig.add_axes([l+0.04, b+0.02, 0.25*w, 0.03])

cb = colorbar(pc, cax=cax, orientation='horizontal') # draw colorbar
cb.set_label('pH')
cb.ax.xaxis.set_label_position('top')
cb.ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
xtl = numpy.round(numpy.linspace(cmin, cmax, 10), decimals=1)
cb.ax.set_xticklabels([xtl[1], xtl[3], xtl[5], xtl[7], xtl[9]])
# cb.ax.set_xticklabels([12., 16., 20., 24., 28.])

# ax.plot returns a list of lines, so unpack tuple
# l1, = ax.plot_date(dt, wd, fmt='k-')
# l1.set_label('Water Level')

ax.set_ylabel('Depth (m)')
ax.set_ylim(-4.,0.)
# first to last regardless of what
# ax.set_xlim(dt[0], dt[-1])
# last minus 30 days, 
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )

ax.set_xlabel('Morgan Bay AVP -- Last 30 days from ' + last_dt_str)

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) meters to (rhs) feet
feet = [procutil.meters2feet(val) for val in ax.get_ylim()]
ax2.set_ylim(feet)
ax2.set_ylabel('Depth (ft)')

# save figure
savefig('/home/haines/rayleigh/img/morgan_avp_last30days.png')

#######################################
# Last 7 days
#######################################

print ' ... Last 7 days'
for i in [0, 1, 2, 3, 4]:
    ax = axs[i]
    ax.set_xlim(date2num(dt[-1])-7, date2num(dt[-1]))
    ax.xaxis.set_major_locator( DayLocator(range(1,32,1)) )
    ax.xaxis.set_minor_locator( HourLocator(range(0,25,6)) )
    ax.set_xticklabels([])
    if i==0:
        ax.set_xlabel('Morgan Bay AVP -- Last 7 days from ' + last_dt_str)
# 

ax = axs[5]
ax.set_xlim(date2num(dt[-1])-7, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(1,32,1)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,6)) )
ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
ax.set_xlabel('Morgan Bay AVP -- Last 7 days from ' + last_dt_str)

savefig('/home/haines/rayleigh/img/morgan_avp_last07days.png')

#######################################
# Last 1 day (24hrs)
#######################################

print ' ... Last 1 days'

for i in [0, 1, 2, 3, 4]:
    ax = axs[i]
    ax.set_xlim(date2num(dt[-1])-1, date2num(dt[-1]))
    ax.xaxis.set_major_locator( HourLocator(range(0,25,1)) )
    ax.xaxis.set_minor_locator( MinuteLocator(range(0,61,30)) )
    ax.set_xticklabels([])
    if i==0:
        ax.set_xlabel('Morgan Bay AVP -- Last 24 hours from ' + last_dt_str)

ax = axs[5]
ax.set_xlim(date2num(dt[-1])-1, date2num(dt[-1]))
ax.xaxis.set_major_locator( HourLocator(range(0,25,1)) )
ax.xaxis.set_minor_locator( MinuteLocator(range(0,61,30)) )
ax.xaxis.set_major_formatter( DateFormatter('%H') )
ax.set_xlabel('Morgan Bay AVP -- Last 24 hours from ' + last_dt_str)

savefig('/home/haines/rayleigh/img/morgan_avp_last01days.png')

