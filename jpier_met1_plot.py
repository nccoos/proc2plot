#!/usr/bin/env /opt/env/haines/dataproc/bin/python
# Last modified:  Time-stamp: <2012-05-14 15:27:38 haines>
"""jpier_met_plot1"""

import os, sys
import datetime, time, dateutil.tz
import pycdf
import numpy

sys.path.append('/opt/env/haines/dataproc/raw2proc')
del(sys)

os.environ["MPLCONFIGDIR"]="/home/haines/.matplotlib/"

from pylab import figure, twinx, savefig, setp, getp, cm, colorbar
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, DateFormatter, date2num, num2date
import procutil

print 'jpier_met_plot1 ...'
prev_month, this_month, next_month = procutil.find_months(procutil.this_month())
#ncFile1='/seacoos/data/nccoos/level1/jpier/met/jpier_met_2008_02.nc'
#ncFile2='/seacoos/data/nccoos/level1/jpier/met/jpier_met_2008_03.nc'

ncFile1='/seacoos/data/nccoos/level1/jpier/met/jpier_met_'+prev_month.strftime('%Y_%m')+'.nc'
ncFile2='/seacoos/data/nccoos/level1/jpier/met/jpier_met_'+this_month.strftime('%Y_%m')+'.nc'

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
ap = nc.var('air_pressure')[:]
at = nc.var('air_temp')[:]
dp = nc.var('dew_temp')[:]
h = nc.var('humidity')[:]
p = nc.var('rainfall_day')[:]
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
ap = numpy.ma.masked_where(numpy.isnan(ap), ap)

# ax.plot returns a list of lines, so unpack tuple
l1, = ax.plot_date(dt, ap, fmt='b-')
l1.set_label('Barometric Pressure')

ax.set_ylabel('Pressure (mbar)')
ax.set_ylim(980.,1040.)
# ax.set_xlim(dt[0], dt[-1]) # first to last regardless of what  
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1])) # last minus 30 days to last
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.set_xticklabels([])

# this only moves the label not the tick labels
ax.xaxis.set_label_position('top')
ax.set_xlabel('JPIER Met -- Last 30 days from ' + last_dt_str)

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) mbar to (rhs) in Hg
inHG = [procutil.millibar2inches_Hg(val) for val in ax.get_ylim()]
ax2.set_ylim(inHG)
ax2.set_ylabel('Pressure (in Hg)')

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
at = numpy.ma.masked_where(numpy.isnan(at), at)


# ax.plot returns a list of lines, so unpack tuple
l1, = ax.plot_date(dt, at, fmt='b-')
l1.set_label('Air Temperature')

l2, = ax.plot_date(dt, dp, fmt='g-')
l2.set_label('Dew Point')

ax.set_ylabel('Temp (deg C)')
ax.set_ylim(-10.,40.)
# ax.set_xlim(dt[0], dt[-1]) 
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
ax.set_xticklabels([])

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) deg C to (rhs) deg F

f = [procutil.celsius2fahrenheit(val) for val in ax.get_ylim()]
ax2.set_ylim(f)
ax2.set_ylabel('Temp (deg F)')

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
ax = fig.add_subplot(4,1,3)
axs.append(ax)

# use masked array to hide NaN's on plot
h = numpy.ma.masked_where(numpy.isnan(h), h)


# ax.plot returns a list of lines, so unpack tuple
l1, = ax.plot_date(dt, h, fmt='b-')
l1.set_label('Relative Humidity')


ax.set_ylabel('RHUM (%)')
ax.set_ylim(0.,100.)
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1])) # last minus 30 days to last
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.set_xticklabels([])

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# no cenversion needed
ylim = [(val) for val in ax.get_ylim()]
ax2.set_ylim(ylim)
ax2.set_ylabel('RHUM (%)')



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
ax = fig.add_subplot(4,1,4)
axs.append(ax)

# use masked array to hide NaN's on plot
p = numpy.ma.masked_where(numpy.isnan(p), p)

# ax.plot returns a list of lines, so unpack tuple
l1, = ax.plot_date(dt, p, fmt='b-')
l1.set_label('Daily Precipitation')

ax.set_ylabel('Rain (mm/day)')
ax.set_ylim(0.,40.)
# last minus 30 days, 
ax.set_xlim(date2num(dt[-1])-30, date2num(dt[-1]))
ax.xaxis.set_major_locator( DayLocator(range(2,32,2)) )
ax.xaxis.set_minor_locator( HourLocator(range(0,25,12)) )
ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )

# right-hand side scale
ax2 = twinx(ax)
ax2.yaxis.tick_right()
# convert (lhs) mm/day to (rhs) in/day
ylim = [procutil.millimeters2inches(val) for val in ax.get_ylim()]
ax2.set_ylim(ylim)
ax2.set_ylabel('Rain (in/day)')


ax.set_xlabel('JPIER Met -- Last 30 days from ' + last_dt_str)

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

# save figure
savefig('/home/haines/rayleigh/img/jpier_met_last30days.png')



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
                ax.set_xlabel('JPIER Met -- Last 30 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('JPIER Met -- Last 30 days from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/jpier_met_last30days.png')


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
                ax.set_xlabel('JPIER Met -- Last 7 days from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%m/%d') )
                ax.set_xlabel('JPIER Met -- Last 7 days from ' + last_dt_str)
                
        savefig('/home/haines/rayleigh/img/jpier_met_last07days.png')


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
                ax.set_xlabel('JPIER Met -- Last 24 hours from ' + last_dt_str)
            elif idx==len(axs)-1:
                ax.xaxis.set_major_formatter( DateFormatter('%H') )
                ax.set_xlabel('JPIER Met -- Last 24 hours from ' + last_dt_str)

        savefig('/home/haines/rayleigh/img/jpier_met_last01days.png')





