#!/usr/bin/env python
# Last modified:  Time-stamp: <2008-10-03 11:35:27 haines>
"""stones_met_plot"""

import os, sys
import datetime, time, dateutil.tz
import pycdf
import numpy

sys.path.append('/home/haines/nccoos/raw2proc')
del(sys)

os.environ["MPLCONFIGDIR"]="/home/haines/.matplotlib/"

from pylab import figure, twinx, savefig, setp, getp, cm, colorbar
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, DateFormatter, date2num, num2date
import procutil

print 'stones_met_plot2 ...'
prev_month, this_month, next_month = procutil.find_months(procutil.this_month())
#ncFile1='/seacoos/data/nccoos/level1/stones/met/stones_met_2008_01.nc'
#ncFile2='/seacoos/data/nccoos/level1/stones/met/stones_met_2008_02.nc'

ncFile1='/seacoos/data/nccoos/level1/stones/met/stones_met_'+prev_month.strftime('%Y_%m')+'.nc'
ncFile2='/seacoos/data/nccoos/level1/stones/met/stones_met_'+this_month.strftime('%Y_%m')+'.nc'

# load data
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
#print ncvars
es = nc.var('time')[:]
units = nc.var('time').units
dt = [procutil.es2dt(e) for e in es]
# set timezone info to UTC (since data from level1 should be in UTC!!)
dt = [e.replace(tzinfo=dateutil.tz.tzutc()) for e in dt]
# return new datetime based on computer local
dt_local = [e.astimezone(dateutil.tz.tzlocal()) for e in dt]
dn = date2num(dt)
ws = nc.var('wspd')[:]
wd = nc.var('wdir')[:]
u = nc.var('wspd')[:]
v = nc.var('wspd')[:]

i = 0
for val in ws:	
	u[i] = -1.*procutil.wind_vector2u(ws[i],wd[i])
	v[i] = -1.*procutil.wind_vector2v(ws[i],wd[i])
        i += 1
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

fig = figure(figsize=(10, 8))
fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.1)

#######################################
# Last 30 days
#######################################
print ' ... Last 30 days'

ax = fig.add_subplot(4,1,1)
axs = [ax]

# use masked array to hide NaN's on plot
wd = numpy.ma.masked_where(numpy.isnan(wd), wd)

# ax.plot returns a list of lines, so unpack tuple
l1, = ax.plot_date(dt, wd, fmt='b-')
l1.set_label('Wind from Direction')

ax.set_ylabel('Dir (true N)')
ax.set_ylim(0.,360.)
# ax.set_xlim(dt[0], dt[-1]) # first to last regardless of what  
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1])) # last minus 30 days to last
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.set_xticklabels([])

# this only moves the label not the tick labels
ax.xaxis.set_label_position('top')
ax.set_xlabel('STONES BAY WIND -- Last 30 days from ' + last_dt_str)

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

# use masked array to hide NaN's on plot
ws = numpy.ma.masked_where(numpy.isnan(ws), ws)


# ax.plot returns a list of lines, so unpack tuple
l1, = ax.plot_date(dt, ws, fmt='b-')
l1.set_label('Wind Speed')


ax.set_ylabel('Speed (m/s)')
ax.set_ylim(0.,20.)

ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1])) # last minus 30 days to last
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.set_xticklabels([])

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) m/s to (rhs) knots
k = [procutil.meters_sec2knots(val) for val in ax.get_ylim()]
ax2.set_ylim(k)
ax2.set_ylabel('Speed (knots)')

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

# use masked array to hide NaN's on plot
# u = numpy.ma.masked_where(numpy.isnan(u), u)
# v = numpy.ma.masked_where(numpy.isnan(v), v)

dt0 = numpy.zeros(len(dt))

ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
ax.axhline(y=0, color='gray')
# make stick plot (set all head parameters to zero)
# scale to y-axis using units='height' of plot with scale = 40 (m/s range) per height with min=-20 and max=20
q1 = ax.quiver(date2num(dt), dt0, u, v, units='height', scale=40, headwidth=0, headlength=0, headaxislength=0)
qk = ax.quiverkey(q1, 0.1, 0.8, 10, r'10 m s-1')

ax.set_ylim(-20.,20.)
ax.set_ylabel('Speed (m/s)')

ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) m/s to (rhs) knots
k = [(val * 1.94384449) for val in ax.get_ylim()]
ax2.set_ylim(k)
ax2.set_ylabel('Speed (knots)')

ax.set_xlabel('STONES BAY WIND -- Last 30 days from ' + last_dt_str)

# save figure
savefig('/home/haines/rayleigh/img/stones_met_last30days.png')

#######################################
# Last 7 days
#######################################

print ' ... Last 7 days'
ax = axs[0]
ax.set_xlim(date2num(dt[-1])-7, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(0,32,1)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,6)) )
ax.set_xticklabels([])
ax.set_xlabel('STONES BAY WIND -- Last 7 days from ' + last_dt_str)

ax = axs[1]
ax.set_xlim(date2num(dt[-1])-7, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(0,32,1)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,6)) )
ax.set_xticklabels([])

ax = axs[2]
ax.set_xlim(date2num(dt[-1])-7, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(0,32,1)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,6)) )
ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
ax.set_xlabel('STONES BAY WIND  -- Last 7 days from ' + last_dt_str)

savefig('/home/haines/rayleigh/img/stones_met_last07days.png')

#######################################
# Last 1 day (24hrs)
#######################################

print ' ... Last 1 days'

ax = axs[0]
ax.set_xlim(date2num(dt[-1])-1, date2num(dt[-1]))
ax.xaxis.set_major_locator( HourLocator(range(0,25,1)) )
ax.xaxis.set_minor_locator( MinuteLocator(range(0,61,30)) )
ax.set_xticklabels([])
ax.set_xlabel('STONES BAY WIND -- Last 24 hours from ' + last_dt_str)

ax = axs[1]
ax.set_xlim(date2num(dt[-1])-1, date2num(dt[-1]))
ax.xaxis.set_major_locator( HourLocator(range(0,25,1)) )
ax.xaxis.set_minor_locator( MinuteLocator(range(0,61,30)) )
ax.set_xticklabels([])

ax = axs[2]
ax.set_xlim(date2num(dt[-1])-1, date2num(dt[-1]))
ax.xaxis.set_major_locator( HourLocator(range(0,25,1)) )
ax.xaxis.set_minor_locator( MinuteLocator(range(0,61,30)) )
ax.xaxis.set_major_formatter( DateFormatter('%H') )
ax.set_xlabel('STONES BAY WIND -- Last 24 hours from ' + last_dt_str)

savefig('/home/haines/rayleigh/img/stones_met_last01days.png')

