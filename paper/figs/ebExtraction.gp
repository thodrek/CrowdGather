set ter postscript enhanced color eps "Helvetica" 30
set output "ebExtraction.eps"
set boxwidth 0.9 absolute
set title "{/Helvetica-Bold Extraction Performance for Eventbrite"
set xlabel  "Budget"
set ylabel  "Extracted Events"
set datafile missing "-"
set key outside center bottom horizontal
set grid x y
set xtics (0,10,20,50,80,100)
set ytics (0,100,300,500,700)
set xrange [0:105]
set yrange [0:700]
set tics out
plot "ebExtraction.txt" using 1:2:3 with yerrorbars ls 1 pt 6 ps 3 lw 4 lt 2 lc 1 title "Rand", \
     "ebExtraction.txt" using 1:4:5 with yerrorbars ls 2 pt 3 ps 3 lw 4 lt 2 lc 7 title "RandL", \
     "ebExtraction.txt" using 1:6:7 with yerrorbars ls 3 pt 1 ps 3 lw 4 lt 2 lc 8 title "BFS", \
     "ebExtraction.txt" using 1:8:9 with yerrorbars ls 4 pt 2 ps 3 lw 4 lt 2 lc 0 title "GSChao", \
     "ebExtraction.txt" using 1:10:11 with yerrorbars ls 5 pt 4 ps 3 lw 4 lt 2 lc 5 title "GSHwang", \
     "ebExtraction.txt" using 1:12:13 with yerrorbars ls 6 pt 5 ps 3 lw 4 lt 2 lc 3 title "GSNewR"