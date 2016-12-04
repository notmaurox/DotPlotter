# DotPlotter
Python program that aligns 2 sequence2, creates a dotplot, and outputs BED file of indel regions

# Input
A .fasta file containing two sequences
# Output
alignmentInfo.txt - contains two sequences after alignment containing "-", also contains alignment score at bottom of file
indelRegions.bed  - depending on provided indel size, this contains info reguarding the indexs where indel regions >= to size provided exist within each sequence informat SequenceID indexStart indexStop

# Usage 
Python3 dotPlotter.py filename.fasta

# Notes
Uses BioPython for global sequence alignment and reading fasta files
Files starting with "ch11_" contain implementation of the graph itself from Bioinformatics Programming Using Python, First Edition (2009)
by Mitchell L Model
