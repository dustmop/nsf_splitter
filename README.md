# NSFSplitter

Splits an exported NSF asm file into multiple files. Useful for dividing music data up into different banks.

## Usage

Open your .ftm file in Famitracker. Export it using "Create NSF" -> "Export As" -> "ASM - Assembly Source" saving the output as "music.asm"

Run this program:

> python nsf_splitter.py music.asm 8,14 result_%d.asm

It splits the file music.asm into 3 files:

* result_0.asm : contains tracks 0..7
* result_1.asm : contains tracks 8..13
* result_2.asm : contains tracks 14..rest
