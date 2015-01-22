set ter postscript enhanced color eps "Helvetica" 30
set output "overlaps.eps"
set boxwidth 5.0 relative
set title "{/Helvetica-Bold Pairwise Overlap \n {/Helvetica-Bold for the 10 Largest Eventbrite Nodes"
set xlabel  "Node-Pair Index"
set ylabel  "Jaccard Index"
set datafile missing "-"
unset key
set grid x y
set autoscale x
set autoscale y
#set xtics (0,10,20,50,80,100)
#set ytics (0,400,800,1200,1600)
#set xrange [0:105]
#set yrange [0:1600]
set tics out
plot "overlaps.txt" using 1:2 ls 7 pt 11 ps 3 lw 4 lt 2 lc 0