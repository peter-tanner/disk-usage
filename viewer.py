
from drive import Drive
from pygnuplot import gnuplot
from utils import nextWeek
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path("/home/peter/scripts/datalogging/disk-usage/testfiles/")
SIZE_FILE = BASE.joinpath("size_daily.csv")
DIFF_FILE = BASE.joinpath("diff_daily.csv")
WEEKLY_SIZE_FILE = BASE.joinpath("size_weekly.csv")
WEEKLY_DIFF_FILE = BASE.joinpath("diff_weekly.csv")

NOW = datetime.now().isoformat(sep="_")

__MAX = nextWeek()   # Next monday
T_MAX = __MAX.isoformat()
T_MIN = (__MAX - timedelta(days=28)).isoformat()
TY_MIN = (__MAX - timedelta(days=364)).isoformat()

Y_MAX = Drive.getMaxTotal("/mnt/")

def fmtRange(min, max):
    return str.format("['{0}':'{1}']", min, max)

array = ""
with open(SIZE_FILE) as f:
    array = f.readline()
array = array.replace(","," ").strip()
HEADER_LENGTH = len(array.split(' '))


PLOT_INIT="""
set terminal sixelgd background rgb 'black' size 1920, 960; set multiplot layout 2,2; set encoding utf8;
set key top left; set key tc rgb 'white'; set border lc rgb 'white'; set key tc rgb 'white'; set datafile separator ',';

set grid ytics; set ytics scale 2,1;

set xdata time; set x2data time; set timefmt '%Y-%m-%d_%H:%M:%S'; set x2label 'Date' textcolor 'white';

set border lc rgb 'white';
"""

PLOT_28D="""
set format x '%Y-%m-%d';
set xtics font ', 10' rotate by 90 right;
set x2tics 4*24*60*60, 7*24*60*60 textcolor 'white';
set x2tics format '%Y-%m-%d';
set x2tics scale 37,1;
set y2tics scale 2,1;
set tics nomirror;

set xlabel 'Day' textcolor 'white';
set xtics 12*60*60, 24*60*60;
set xtics format '%a';
set mxtics 2;
set xtics scale 0,1;
set grid mxtics;
"""

# Some bug with scaling meant that I needed to use 59.999999999999 as opposed to
# 60 for the offsets of the weeks from the months IIRC. Haven't checked if this
# bug is still here.
PLOT_364D="""
set x2tics font ', 10';
set x2tics 11*24*60*60, 3*7*24*60*60+7*24*60*59.999999999999 textcolor 'white';
set x2tics format '%m-%d';
set x2tics scale 2,1;
set mx2tics 4;

set xlabel 'Month' textcolor 'white';
set xtics 4*7*24*60*60;
set xtics format '%b';
set xtics font ', 10' rotate by 0 center;
set mxtics 1;
set xtics scale 1,1;
set grid xtics;
"""

PLOT_DIFF = """
set autoscale y
set ylabel '{/Symbol D}Used [SI definition]' textcolor 'white';
set format y '%+08.3s %cB';

set y2label '{/Symbol D}Used (GB)' textcolor 'white';
set link y2 via y/(1024**3) inverse y*(1024**3);
set format y2 '%+08.3s %c';
"""
	
PLOT_0="""set title 'Used capacity of disks (last 28 days)' textcolor 'white';

set format y '%.2s %cB';
set ylabel 'Used [SI definition]' textcolor 'white';
set ytics 0.25*10**12;
set mytics 2;

set link y2 via y/1024**4 inverse y*1024**4;
set format y2 '%05.3f';
interval = (2.5*10**11)/(1024**4); set y2tics interval;
set y2label 'Used (TB)' textcolor 'white';
set my2tics 1;
"""

# 
# plot for [col=3:$columns] '$(sed 's/\///1;s/\//:\//1' <<< "$FILE")' using 1:col with linespoints title word(array, col) pointtype 5"""

PLOT_1="""
set title 'Change in used capacity (last 28 days)' textcolor 'white';

set ytics 5*10**9;
set mytics 2;

interval = (5.0*10**9)/(1024**3); set y2tics interval;
set my2tics 2;

set offset graph 0, graph 0, graph 0.02, graph 0.02;
"""+PLOT_DIFF

PLOT_2="""
set title 'Used capacity of disks (last 364 days)' textcolor 'white';

set ylabel 'Used [SI definition]' textcolor 'white';
set format y '%.2s %cB';
set ytics 0.25*10**12;
set mytics 2;

set y2label 'Used (TB)' textcolor 'white';
set link y2 via y/1024**4 inverse y*1024**4;
set format y2 '%05.3f';
interval = (2.5*10**11)/(1024**4); set y2tics interval;
set my2tics 1;

set offset graph 0, graph 0, graph 0, graph 0;
"""


PLOT_3="""
set title 'Change in used capacity (last 364 days)' textcolor 'white';

set ytics 10*10**9;
set mytics 2;

interval = (10.0*10**9)/(1024**3); set y2tics interval;
set my2tics 2;

set offset graph 0, graph 0, graph 0.02, graph 0.02;
"""+PLOT_DIFF

g = gnuplot.Gnuplot(out = '"test.six"')
g.cmd(PLOT_INIT)

# Reset line colors cycle
columns = 3
g.set(linetype = "cycle "+str(columns-2))
for i in range(columns,9):
    g.unset("linetype "+str(i))

# set up ranges 28d
g.set(
    yrange =  fmtRange(0,Y_MAX),
    xrange =  fmtRange(T_MIN,T_MAX),
    x2range = fmtRange(T_MIN,T_MAX),
)
g.cmd(PLOT_28D)
g.set(
    arrow  = "1 from first '"+NOW+"',graph 0 to first '"+NOW+"',graph 1 nohead lw 1.5 dt 2 lc rgb '#00000099'",
    object = "1 rect from '"+NOW+"',graph 0 to graph 1, graph 1 fc rgb '#00444444' fillstyle pattern 4 noborder transparent"
) # PLOT_CROSS

PLOT_RANGE = "for [col=3:"+str(HEADER_LENGTH)+"]"

g.cmd(PLOT_0)
g.cmd("plot "+PLOT_RANGE+" '"+SIZE_FILE.as_posix()+"' using 1:col with linespoints title word('"+array+"', col) pointtype 5 pointsize 0.5")
g.cmd(PLOT_1)
g.cmd("plot "+PLOT_RANGE+" '"+WEEKLY_DIFF_FILE.as_posix()+"' using 1:col-1 with linespoints title word('"+array+"', col) pointtype 5, \
	        "+PLOT_RANGE+" '"+DIFF_FILE.as_posix()+"' using 1:col with points notitle pointtype 12 pointsize 2")
# set up ranges 365d
g.set(
    yrange =  fmtRange(0,Y_MAX),
    xrange =  fmtRange(TY_MIN,T_MAX),
    x2range = fmtRange(TY_MIN,T_MAX),
)
g.cmd(PLOT_364D)
g.cmd(PLOT_2)
g.cmd("plot "+PLOT_RANGE+" '"+WEEKLY_SIZE_FILE.as_posix()+"' using 1:col-1 with linespoints title word('"+array+"', col) pointtype 5")
g.cmd(PLOT_3)
g.cmd("plot "+PLOT_RANGE+" '"+WEEKLY_DIFF_FILE.as_posix()+"' using 1:col-1 with linespoints title word('"+array+"', col) pointtype 5")
