import numpy
import h5py
import sys, time, os, math, re

def real_time_scheduling():
    r = gr.enable_realtime_scheduling()
    if r == gr.RT_OK:
        print("Realtime scheduling enabled")
    else:
        print "Note: failed to enable realtime scheduling"

# lots of metadata...
def write_metadata(dirn, n_channels, center_freqs, ut0, dtype="<i2", itemsize=4, sr=100000000, extra_keys=[],extra_values=[]):
    f = h5py.File("%s/sampler_config.hdf5"%(dirn),'w')

    f["version"] = "2.0"
    f["sample_rate"] = float(sr)
    f["sample_period_ps"] = int(1000000000000/int(sr))
    f["center_frequencies"] = numpy.array(center_freqs)
    f["t0"] = ut0
    f["n_channels"] = n_channels
    f["itemsize"] = itemsize
    f["dtype"] = dtype

    for ki in numpy.arange(len(extra_keys)):
        f[extra_keys[ki]] = extra_values[ki]
        
    f.close()
def write_metadata_drf(dirn, n_channels, center_freqs, ut0, dtype="<i2", itemsize=4, sr=100000000, extra_keys=[],extra_values=[]):
    f = h5py.File("%s/metadata@%1.3f.h5"%(dirn,ut0),'w')

    f["sampler_version"] = "1.0"
    f["sample_rate"] = float(sr)
    f["sample_period_ps"] = int(1000000000000/int(sr))
    f["center_frequencies"] = numpy.array(center_freqs)
    f["t0"] = ut0
    f["n_channels"] = n_channels
    f["itemsize"] = itemsize
    f["dtype"] = dtype

    for ki in numpy.arange(len(extra_keys)):
        f[extra_keys[ki]] = extra_values[ki]
        
    f.close()

# make a string with time stamp
def time_stamp():
    a=time.time()
    b=time.strftime("%Y.%m.%d_%H.%M.%S",time.strptime(time.ctime(a)))
    stmp="%s.%09d" % (b,int((a-math.floor(a))*1000000000))
    return(stmp)

# find next time when to latch into a loop that started at ut0 (unix seconds) and has period per.
def find_next(t0,per=120):
    a=time.time()+5
    i = 0
    while t0+per*i < a:
        i = i + 1
    print "Launch at ",time.ctime(t0+per*i)
    return(t0+per*i)

def latch_usrp_to_pps(usrp):
    usrp.set_clock_source("external", uhd.ALL_MBOARDS)
    usrp.set_time_source("external", uhd.ALL_MBOARDS)
    # wait until time 0.2 to 0.5 past full second, then latch.
    # we have to trust NTP to be 0.2 s accurate. It might be a good idea to do a ntpdate before running
    # uhdsampler.py
    tt = time.time()
    while tt-math.floor(tt) < 0.2 or tt-math.floor(tt) > 0.3:
        tt = time.time()
        time.sleep(0.01)
    usrp.set_time_unknown_pps(uhd.time_spec(math.ceil(tt)+1.0))

def make_tstamped_dir(prefix="data"):
    dirname="%s-%s" % (prefix,time_stamp())
    os.mkdir(dirname)
    os.chdir(dirname)


