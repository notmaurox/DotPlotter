import tkinter
from ch11_dotplot import DotPlot
from Bio import pairwise2
from Bio.pairwise2 import format_alignment
from Bio import SeqIO
import sys
import os

if __name__ == '__main__':
    if len(sys.argv)!=5:
        print("ERROR: Incorrect number of arguements")
        print("USAGE:")
        print("python3 dotPlotter.py <fasta_file> <indel size threshold> <window size> <count threshold>")
        quit()

    if not os.path.exists('dotPlotterOut'):
        os.makedirs('dotPlotterOut')

    seqAid = ""
    seqA = ""
    seqBid = ""
    seqB = ""
    fasta_sequences = SeqIO.parse(open(sys.argv[1]),'fasta')
    fastasRead = 0
    for fasta in fasta_sequences:
            if fastasRead == 0:
                seqAid, seqA = fasta.id, str(fasta.seq)
                fastasRead += 1
            if fastasRead == 1:
                seqBid, seqB = fasta.id, str(fasta.seq)

    alignments = pairwise2.align.globalxx(seqA,seqB)

    file = open("dotPlotterOut/alignmentInfo.txt", "w")
    file.write( format_alignment(*alignments[0]) )
    file.close()
    print("wrote dotPlotterOut/alignmentInfo.txt")

    file = open('dotPlotterOut/alignmentInfo.txt', 'r')

    seqAalign = ""
    seqBalign = ""
    alignScore = 0

    for i in range(1,5):
        line = file.readline()
        if( i == 1 ):
            seqAalign = line
        if( i == 3 ):
            seqBalign = line
        if( i == 4):
            alignScore = int( line.replace('\n','')[8:len(line)] )
    file.close()

    seqAalign = seqAalign.replace('\n', '')
    seqBalign = seqBalign.replace('\n', '')

    #Build BED File:
    size = int(sys.argv[2])
    file = open("dotPlotterOut/indelRegions.bed", "w")
    startCount = False
    start = 0
    stop = 0
    for i in range(len(seqAalign)):
        if( seqAalign[i] == "-" and startCount == False):
            startCount = True
            start = i
        if( seqAalign[i] != "-" and startCount == True):
            startCount = False
            stop = i
            if( (stop-start) >= size):
                file.write( seqAid + " " + str(start) + " " + str(stop) )
                file.write( "\n" )
    startCount = False
    start = 0
    stop = 0
    for i in range(len(seqBalign)):
        if( seqBalign[i] == "-" and startCount == False):
            startCount = True
            start = i
        if( seqBalign[i] != "-" and startCount == True):
            startCount = False
            stop = i
            if( (stop-start) >= size):
                file.write( seqBid + " " + str(start) + " " + str(stop) )
                file.write( "\n" )
    file.close()
    print("wrote dotPlotterOut/indelRegions.bed")

    ## Window = w, the length of the diagonal window from given point
    ## Cutoff = c, the number of points in that given window
    ## At each point, that point is compared to the next w-1 points, the total
    ## Number of matches is counted. A match between two of the same neucleotide
    ## is only regestered when the count is at least c.
    ## Amino acid seq w=3 and t =2
    ## Base sequences w=11 and c=7

    w = int(sys.argv[3])
    t = int(sys.argv[4])


    plot = DotPlot(seqAalign, seqBalign, window=w, threshold=t, with_axes=True,
                   ps_filename='dotPlotterOut/dotplot.ps', ps_scale=0.6)
    plot.execute()
    try:
        sys.ps1                     # are we running interactively?
    except:                         # no
        input("Press the Return key to close the window(s)")
        plot.close()
