set ter postscript enhanced color eps "Helvetica" 30
set output "eventbritepop.eps"
set boxwidth 5.0 relative
set title "{/Helvetica-Bold Eventbrite Domain Population"
set xlabel  "Poset Node Index (x 10^3)"
set ylabel  "Number of Events in Node"
set datafile missing "-"
unset key
set grid x y
set autoscale x
set autoscale y
set logscale y
set format y "10^{%L}"
set format x "%.0s”
#set xtics (0,10,20,50,80,100)
#set ytics (0,400,800,1200,1600)
#set xrange [0:105]
#set yrange [0:1600]
set tics out
plot "eventbritepop.txt" using 1:2 ls 7 pt 11 ps 3 lw 4 lt 2 lc 0