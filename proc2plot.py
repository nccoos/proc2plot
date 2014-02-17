#!/usr/bin/env python
# Last modified:  Time-stamp: <2014-02-04 13:32:11 haines>
"""Create plots from monthly netCDF data files

This module plots different graphical products from different NCCOOS
sensors (ctd, adcp, waves-adcp, met) based on manual or automated
operation.  If automated processing, latest and current month plots
are generated for all active sensors based on the current
configuration setting.  If manual processing, generate graphics for
requested platform, sensor, and month.

:Processing steps:
  0. proc2plot auto or manual for platform, sensor, month
  1. 

added spin cycle
removed redundant functions that are in raw2proc module

"""

__version__ = "v0.1"
__author__ = "Sara Haines <sara_haines@unc.edu>"

import sys
import os
import re

# for testing use:
# defconfigs='/home/haines/nccoos/test/r2p'

# define config file location to run under cron
defconfigs='/opt/env/haines/dataproc/raw2proc'

import numpy

sys.path.append('/opt/env/haines/dataproc/raw2proc')
del(sys)

from raw2proc import *
from procutil import *
from ncutil import *        

def proc2plot(proctype, platform=None, package=None, yyyy_mm=None):
    """
    Plot products either in auto-mode or manual-mode

    If auto-mode, process latest products for all platforms, all
    sensors. Otherwise in manual-mode, process data for specified
    platform, sensor package, and month.

    :Parameters:
       proctype : string
           'auto' or 'manual'

       platform : string
           Platfrom id to process (e.g. 'bogue')
       package : string
           Sensor package id to process (e.g. 'adcp')
       yyyy_mm : string
           Year and month of data to process (e.g. '2007_07')

    Examples
    --------
    >>> proc2plot(proctype='manual', platform='bogue', package='adcp', yyyy_mm='2007_06')
    >>> proc2plot('manual', 'bogue', 'adcp', '2007_06')
          
    """
    print '\nStart time for proc2plot: %s\n' % start_dt.strftime("%Y-%b-%d %H:%M:%S UTC")

    if proctype == 'auto':
        print 'Processing in auto-mode, all platforms, all packages, latest data'
        auto()
    elif proctype == 'manual':
        if platform and package and yyyy_mm:
            print 'Processing manually ...'
            print ' ...  platform id : %s' % platform
            print ' ... package name : %s' % package
            print ' ...        month : %s' % yyyy_mm
            print ' ...  starting at : %s' % start_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            manual(platform, package, yyyy_mm)
        else:
            print 'proc2plot: Manual operation requires platform, package, and month'
            print "   >>> proc2plot(proctype='manual', platform='bogue', package='adcp', yyyy_mm='2007_07')"
    elif proctype == 'spin':
        if platform and package and yyyy_mm:
            print 'Processing in spin-mode ...'
            print ' ...  platform ids : %s' % platform
            print ' ... package names : %s' % package
            print ' ...        months : %s' % yyyy_mm
            print ' ...   starting at : %s' % start_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            spin_list = create_spin_list(platform, package, yyyy_mm)
            spin(spin_list)
        else:
            print "proc2plot: Spin operation requires platform(s), package(s), and month(s)"
            print "   >>> proc2plot(proctype='spin', platform='b1', package='ALL', yyyy_mm='ALL')"
            print "   >>> proc2plot(proctype='spin', platform='ALL', package='met', yyyy_mm='2011_11')"
            print "   >>> proc2plot('spin', ['b1','b2'], ['ctd1', 'ctd2'], [datetime(2011,11,1), datetime(2012,4,1)])"
    else:
        print 'proc2plot: requires either auto or manual or sping operation'


def auto():
    """Process all platforms, all packages, latest data

    Notes
    -----
    
    1. determine which platforms (all platforms with currently active
       config files i.e. config_end_date is None
    2. for each platform
         get latest config
         for each package
           yyyy_mm is the current month
           load this months netcdf
           load and execute plot module(s) 
           
    """
    yyyy_mm = this_month()
    months = find_months(yyyy_mm)
    month_start_dt = months[1]
    month_end_dt = months[2] - timedelta(seconds=1)

    configs = find_active_configs(config_dir=defconfigs)
    if configs:
        # for each configuration 
        for cn in configs:
            print ' ... config file : %s' % cn
            pi = get_config(cn+'.platform_info')
            asi = get_config(cn+'.sensor_info')
            platform = pi['id']
            # for each sensor package
            for package in asi.keys():
                print ' ... package name : %s' % package
                si = asi[package]
                si['proc_filename'] = '%s_%s_%s.nc' % (platform, package, yyyy_mm)
                ofn = os.path.join(si['proc_dir'], si['proc_filename'])
                si['proc_start_dt'] = month_start_dt
                si['proc_end_dt'] = month_end_dt
                if os.path.exists(ofn):
                    # get last dt from current month file
                    (es, units) = nc_get_time(ofn)
                    last_dt = es2dt(es[-1])
                    # if older than month_start_dt use it instead to only process newest data
                    if last_dt>=month_start_dt:
                        si['proc_start_dt'] = last_dt

                if 'plot_module' in si.keys():
                    make_plots(pi, si, yyyy_mm, plot_type='latest')
                    # determine if any nc_file at this point
                    # and what to do if no files found
                else:
                    print ' ... ... NOTE: no plot module specified for %s %s for %s' % (package, platform, yyyy_mm)


    #
    else:
        print ' ... ... NOTE: No active platforms'

def spin(spin_list):
    """ wrapper to run manual() for multiple platforms, packages, and months"""
    for item in spin_list:
        platform, package, yyyy_mm = item
        proc2plot('manual',platform, package, yyyy_mm)
                            
def manual(platform, package, yyyy_mm):
    """Process data for specified platform, sensor package, and month

    Notes
    -----
    
    1. determine which configs
    2. for each config for specific platform
           if have package in config
               which nc files
    """
     # determine when month starts and ends
    months = find_months(yyyy_mm)
    month_start_dt = months[1]
    month_end_dt = months[2] - timedelta(seconds=1)
   
    configs = find_configs(platform, yyyy_mm, config_dir=defconfigs)

    if configs:
        # for each configuration 
        for index in range(len(configs)):
            cn = configs[index]
            print ' ... config file : %s' % cn
            pi = get_config(cn+'.platform_info')
            # month start and end dt to pi info
            asi = get_config(cn+'.sensor_info')
            if package in pi['packages']:
                si = asi[package]
                if si['utc_offset']:
                    print ' ... ... utc_offset : %g (hours)' % si['utc_offset']
                si['proc_start_dt'] = month_start_dt
                si['proc_end_dt'] = month_end_dt
                si['proc_filename'] = '%s_%s_%s.nc' % (platform, package, yyyy_mm)
                ofn = os.path.join(si['proc_dir'], si['proc_filename'])
                # this added just in case data repeated in data files
                if os.path.exists(ofn):
                    # get last dt from current month file
                    (es, units) = nc_get_time(ofn)
                    last_dt = es2dt(es[-1])

                if 'plot_module' in si.keys():
                    make_plots(pi, si, yyyy_mm, plot_type='monthly')
                    # determine if any nc_file at this point
                    # and what to do if no files found
                else:
                    print ' ... ... NOTE: no plot module specified for %s %s for %s' % (package, platform, yyyy_mm)
                
            else:
                print ' ... ... NOTE: %s not operational on %s for %s' % (package, platform, yyyy_mm)                
    else:
        print ' ... ... ... NOTE: %s not operational for %s' % (platform, yyyy_mm)
    
def import_plotter(mod_name, plot_name):
    mod = __import__(mod_name)
    plotter = getattr(mod, plot_name)
    return plotter

def make_plots(pi, si, yyyy_mm, plot_type='latest'):
    # tailored graphics for different packages and platforms and deployment configurations 
    mod_name = si['plot_module']
    plot_names = si['plot_names']

    for pn in plot_names:
        plot = import_plotter(mod_name, pn)
        plot(pi, si, yyyy_mm, plot_type)

    # ISSUES:
    #   1. how to handle other time spans, besides monthly ... hourly, daily, yearly, record ...
    #   2. specifying data from other sources (besides current month, plat, package) for plots may be addressed by tailored plots
    #   3. other types of plots (maps, wave energy spectrum)

    
# globals
start_dt = datetime.utcnow()
start_dt.replace(microsecond=0)

if __name__ == "__main__":
    import optparse
    proc2plot('auto')

    # for testing 
    # proctype='manual'; platform='bogue'; package='adcp'; yyyy_mm='2007_07'
    # proc2plot(proctype='manual', platform='bogue', package='adcp', yyyy_mm='2007_07')
