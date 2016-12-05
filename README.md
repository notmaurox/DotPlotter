# DotPlotter
Python program that aligns 2 sequence2, creates a dotplot, and outputs BED file of indel regions, txt file showing how sequences were aligned, and postscript file for reopening the graph.

# Input arguements
1) A FASTA file containing two sequences

2) Size threshold for returned indel regions in file [indelRegions.bed](indelRegions.bed)

3) DotPlot window size

4) DotPlot window count threshold

# Output
A graph where the first sequence is along the x-axis and the second along the y-axis. Perfect matches in nucleotides are represented
on the graph as black points. If a match occurs because of two empty spaces ("-" character) it is represented by a red dot.

The following files will be placed within a directory called ``dotPlotterOut``:

* ``alignmentInfo.txt`` - contains two sequences after alignment containing "-", also contains alignment score at bottom of file

* ``indelRegions.bed``  - depending on provided indel size, this contains info reguarding the indices where indel regions >= to
size provided exist within each sequence informat SequenceID indexStart indexStop

* ``dotPlot.ps`` - can be used to reopen the graph once the initial window created by the program has been closed

# Usage
```
python3 dotPlotter.py filename.fasta (indel size threshold) (window size) (count threshold)
```

Specifying the window size (w) and count threshold (t) helps remove
noise from the graph. Window size describes how many spaces along the
diagonal from a match in nucleotides should be considered. If there are
at least t other points on the graph in this diagonal window,
the original point gets drawn.

Recommended settings:

Amino Acid Seq: w = 3 and t = 2

Base Seq:  w = 11 and t = 7

# Notes
Uses BioPython for global sequence alignment and reading fasta files

Files starting with "ch11_" contain implementation of the graph itself from Bioinformatics Programming Using Python, First Edition (2009)
by Mitchell L Model. They were modified slightly to add extra functionality. 
