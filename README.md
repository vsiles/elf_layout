# elf_layout
Author: Vincent Siles <vincent.siles@AT@ens-lyon.org>
Created on: June 30th, 2015

Pie-Chart display of ELF memory footprint.

Relies on python 2.7, readelf and matplotlib.

Usage: 

elf_layout.py --version
    Print current version.
    
elf_layout.py --help
    Print how to use the program.

elf_layout.py [--all] [--filter=X] [--label=str ...] filename.elf
    Analyze ELF file's OBJECT blops.

    filename.elf *has* to be the last argument.

    If [--all] modifier is present, does not restrict the analysis to OBJECT
    entries but to any entry.


    If [--filter] is present, the pie chart won't take into account any entry
    which is bigger than the filter (in ratio).

    If one or several [--label] entries are present, the analysis will try to
    local pairs of labels '_start' '_end' and add fake objects whose size is
    the length of the two addresses. (Not 100% failproof atm)
