#!/usr/bin/env uv run


# 2-1/3" x 3-3/8"

import fileinput

import click
from path import Path

from PIL import Image

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import white, black, lawngreen

from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import simpleSplit

from logo_provider import to_inches, to_mm, LogoProvider

DEBUG = False
CUT_MARKS = False

CARD_SIZE = to_mm(63, 88)

# http://stackoverflow.com/a/1751478/25625
def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]


NAME_STYLE = ParagraphStyle("Name", fontName="Times-Bold", fontSize=24, leading=28, alignment=TA_CENTER)

LOGO = LogoProvider(None, 90, 90, 1)

class Card(object):
    def __init__(self, text, width, height, offset_x, offset_y):
        self.text = text
        self.offset = [offset_x, offset_y]
        self.width = width
        self.height = height

    def draw_background(self, c):
        logo_width, logo_height = LOGO.image_size_raw(self.width, self.height)
        logo_x = 0.15 * logo_width
        logo_width = 0.85 * logo_width
        logo_height = 0.85 * logo_height
        logo_y = (self.height - logo_height) / 2.0
        c.drawImage(LOGO.get_image_reader(), logo_x, logo_y, height=logo_height, width=logo_width, mask='auto')


    def render(self, c):
        c.translate(*self.offset)
        # 0.75" tall, automatic width

        # self.draw_background(c)

        success = False
        name_size = 24
        drop_size = 0
        while not success:
            if name_size - drop_size < 0:
                #raise Exception("Could not possibly fit this even at a tiny size: {}".format(self.card))
                print("Could not possibly fit this even at a tiny size: {}".format(self.card))
                return
            name_style = NAME_STYLE.clone("Name {}".format(name_size-drop_size))
            name_style.fontSize = name_size - drop_size
            name_style.leading = name_size + 4 - drop_size
            lines = []
            lines.append(Paragraph(self.text, name_style))

            text_height = get_text_height(lines, self.width)
            box_top = (self.height - text_height) / 2 + text_height
            if DEBUG and text_height > 0:
                c.rect(0, box_top - text_height - 10, self.width, text_height)
            success = text_height < box_top
            if success:
                success = self.render_frame(0, 0, self.width, box_top, lines, c)
            drop_size += 2

        # Just for debugging
        if DEBUG:
            c.rect(0, 0, self.width, self.height)

        # Show where to cut the cards
        if CUT_MARKS:
            c.rect(0, 0, self.width, self.height)

    def render_frame(self, bottom, left, width, height, lines, canvas):
        # Work on a copy of lines in case we start over
        lines = list(lines)

        frame = Frame(bottom, left, width, height, showBoundary=DEBUG)
        frame.addFromList(lines, canvas)
        if len(lines) > 0:
            # raise Exception("Could not fit all of {}: {}".format(self.card, lines))
            # canvas.setStrokeColor(white)
            #canvas.setFillColor(white)
            #canvas.rect(bottom, left, width, height, stroke=False, fill=True)
            return False
        return True

def get_text_height(lines, width):
    answer = 0
    for line in lines:
        # simpleSplit calculates how reportlab will break up the lines for
        # display in a paragraph, by using width/fontsize.
        # Default Frame padding is 6px on left & right
        split = simpleSplit(line.text, line.style.fontName, line.style.fontSize, width - 12)
        answer += len(split) * line.style.leading
    return answer


class CardReport(object):
    # Defaults are for Avery #5395 8-per-page name tag stickers
    def __init__(self, cards,
            margin_left_bottom_in=(0.75, 5/8.0),
            per_page=9,
            card_class=Card
            ):
        self.cards = cards
        self.margin_left, self.margin_bottom = to_inches(*margin_left_bottom_in)
        self.offset_x, self.offset_y = CARD_SIZE
        self.card_width, self.card_height = CARD_SIZE
        self.per_page = per_page
        self.card_class = card_class
        self.cells = []
        for row in self.row_indices():
            for col in range(3):
                x = self.margin_left + self.offset_x * col
                y = self.margin_bottom + self.offset_y * row
                self.cells.append([x, y])

    def row_indices(self):
        return list(range(int(self.per_page/3)-1, -1, -1))

    def render(self, c):
        x = 0.0
        for page in chunks(self.cards, self.per_page):
            for offset, card in zip(self.cells, page):
                x += 1
                c.saveState()
                self.card_class(card, self.card_width, self.card_height, *offset).render(c)
                c.restoreState()
            c.showPage()
        c.save()

def render_to_filename(items, filename):
    try:
        Path(filename).dirname().makedirs()
    except:
        pass
    c = canvas.Canvas(filename, pagesize=letter)
    ntr = CardReport(items)
    ntr.render(c)
    print("Wrote {}".format(filename))

@click.command()
@click.argument("output-base-name")
@click.argument("card-sources", nargs=-1)
@click.option("--debug/--no-debug")
@click.option("--cut-lines/--no-cut-lines")
def main(output_base_name, card_sources, cut_lines=True, debug=False):
    global DEBUG, CUT_MARKS
    DEBUG = debug
    CUT_MARKS = cut_lines

    if not card_sources:
        print("Using test card text")
        card_sources = ["lorem-cards.txt", "poe-cards.txt"]

    if DEBUG:
        NAME_STYLE.borderWidth = 1
        NAME_STYLE.borderColor = black

    fi = fileinput.input(card_sources)

    cards = [*fi]

    render_to_filename(cards, output_base_name)

if __name__ == '__main__':
    main()

