set ter postscript enhanced color eps "Helvetica" 22
set output "gain_cost.eps"
set boxwidth 2 absolute
set title "{/Helvetica-Bold Total Gain vs. Cost"
set xlabel  "Total Cost"
set ylabel  "Total Extracted Entities"
set grid x y
set datafile missing "-"
set tics out
set key outside bottom center horizontal
plot "gain_cost.dat" using 2:1 pt 1 ps 2 title "RootChao", \
     "gain_cost.dat" using 4:3 lt 0 pt 6 ps 2 title "GSChao", \
     "gain_cost.dat" using 6:5 pt 3 ps 2 title "GSHawng", \
     "gain_cost.dat" using 8:7 lt 13 pt 13 ps 2 title "GSNewR"
