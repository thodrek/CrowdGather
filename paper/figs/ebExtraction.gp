set ter postscript enhanced color eps "Helvetica" 22
set output "ebExtraction.eps"
set boxwidth 2 absolute
set title "{/Helvetica-Bold Extraction Performance for Eventbrite"
set xlabel  "Budget"
set ylabel  "Extracted Events"
set datafile missing "-"
set key outside bottom center horizontal
set grid x y
set xtics (10,20,50,80,100)
#set ytics (0,300,500,700,1600)
set xrange [10:105]
set yrange [0:1600]
set tics out
plot "ebExtraction.txt" using 1:2:3 with linespoints ls 1 pt 6 ps 3 lw 4 lt 1 lc 1 title "Rand", \
     "ebExtraction.txt" using 1:4:5 with linespoints ls 2 pt 3 ps 3 lw 4 lt 1 lc 7 title "RandL", \
     "ebExtraction.txt" using 1:6:7 with linespoints ls 3 pt 1 ps 3 lw 4 lt 1 lc 8 title "BFS", \
     "ebExtraction.txt" using 1:8:9 with linespoints ls 4 pt 2 ps 3 lw 4 lt 1 lc 0 title "GSChao", \
     "ebExtraction.txt" using 1:10:11 with linespoints ls 5 pt 4 ps 3 lw 4 lt 1 lc 5 title "GSHwang", \
     "ebExtraction.txt" using 1:12:13 with linespoints ls 6 pt 5 ps 3 lw 4 lt 1 lc 3 title "GSNewR", \
     "ebExtraction.txt" using 1:14:15 with linespoints ls 3 pt 7 ps 3 lw 4 lt 1 lc 2 title "RootChao"