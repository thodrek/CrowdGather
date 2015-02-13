set ter postscript enhanced color eps "Helvetica" 22
set output "gain_rounds.eps"
set boxwidth 2 absolute
set title "{/Helvetica-Bold Total Gain vs. Number of Queries"
set xlabel  "Total Queries"
set ylabel  "Total Extracted Entities"
set grid x y
set datafile missing "-"
set tics out
set key outside bottom center horizontal
plot "gain_rounds.dat" using 1:2 pt 1 ps 2 title "RootChao", \
     "gain_rounds.dat" using 1:3 lt 0 pt 6 ps 2 title "GSChao", \
     "gain_rounds.dat" using 1:4 pt 3 ps 2 title "GSHawng", \
     "gain_rounds.dat" using 1:5 lt 13 pt 13 ps 2 title "GSNewR"
