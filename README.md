# Text Card Prototyper

Convert one or more text files to 

## Requirements

- Python 3.13 or newer (or maybe bit older)
- [uv](https://docs.astral.sh/uv/#projects) (`brew install uv`)

## Usage

1. Put your cards into a text file with one card per line.
2. Run `./card_generator.py OUTPUT_PDF_NAME.pdf cards.txt --cut-lines`
    - To omit cutting guides, remove `--cut-lines`
    - You can see some sample cards with text of various sizes by omitting the `cards.txt` argument.
    - You can provide several different text files, and they will all be used.

