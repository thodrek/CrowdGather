set ter postscript enhanced color eps "Helvetica" 22
# set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 500, 350 
set output 'queryConfBudget.eps'
set border 3 front linetype -1 linewidth 1.000
set boxwidth 0.8 absolute
set style fill solid 1.00 noborder
set grid 
#set key bmargin center horizontal Left reverse noenhanced autotitles columnhead nobox
unset key
set style histogram rowstacked title  offset character 2, 0.25, 0
set datafile missing '-'
set style data histograms
set xtics border in scale 0,0 nomirror rotate by -45  offset character 0, 0, 0
set xtics  norangelimit font ",22"
set xtics   ()
set ytics border in scale 0,0 mirror norotate  offset character 0, 0, 0
set title "Average Number of Queries for each Configuration, Algorithm, Budget" 
set ylabel "Number of Queries" 
set yrange [0:62] noreverse nowriteback
plot newhistogram "Budget = 10", 'queryConfBudget.txt' using 2:xtic(1) t col lc rgb "blue", '' u 3 t col, '' u 4 t col, '' u 5 t col, newhistogram "Budget = 50", '' u 6:xtic(1) t col, '' u 7 t col, '' u 8 t col, '' u 9 t col, newhistogram "Budget = 100", '' u 10:xtic(1) t col, '' u 11 t col, '' u 12 t col, '' u 13 t col