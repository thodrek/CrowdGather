set ter postscript enhanced color eps "Helvetica" 22
set output "ebExtractionGS.eps"
set boxwidth 2 absolute
set title "{/Helvetica-Bold Extraction Performance for Eventbrite"
set xlabel  "Budget"
set ylabel  "Extracted Events"
set datafile missing "-"
set key outside bottom center horizontal
set grid x y
set xtics (10,20,50,80,100)
set xrange [10:105]
set autoscale y
set tics out
plot "ebExtraction.txt" using 1:8:9 with linespoints ls 4 pt 2 ps 3 lw 4 lt 1 lc 0 title "GSChao", \
     "ebExtraction.txt" using 1:10:11 with linespoints ls 5 pt 4 ps 3 lw 4 lt 1 lc 5 title "GSHwang", \
     "ebExtraction.txt" using 1:12:13 with linespoints ls 6 pt 5 ps 3 lw 4 lt 1 lc 3 title "GSNewR", \
     "ebExtraction.txt" using 1:14:15 with linespoints ls 7 pt 11 ps 3 lw 4 lt 1 lc 2 title "GSExact"