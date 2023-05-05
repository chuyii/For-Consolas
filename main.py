#!/usr/bin/env python3
# pyright: reportUnknownMemberType=false
from __future__ import annotations

import argparse
import json
import math
from typing import TypedDict

import fontforge
import psMat


class FontAttributes(TypedDict):
    em: int
    ascent: int
    descent: int
    upos: int
    uwidth: int
    os2_strikeypos: int
    os2_strikeysize: int
    os2_subxoff: int
    os2_subxsize: int
    os2_subyoff: int
    os2_subysize: int
    os2_supxoff: int
    os2_supxsize: int
    os2_supyoff: int
    os2_supysize: int


CONSOLAS_REGULAR: FontAttributes = {
    "em": 2048,
    "ascent": 1521,
    "descent": 527,
    # 下線
    "upos": -338,
    "uwidth": 144,
    # 取り消し線
    "os2_strikeypos": 512,
    "os2_strikeysize": 102,
    # 下付き文字
    "os2_subxoff": 0,
    "os2_subxsize": 1434,
    "os2_subyoff": 287,
    "os2_subysize": 1331,
    # 上付き文字
    "os2_supxoff": 0,
    "os2_supxsize": 1434,
    "os2_supyoff": 977,
    "os2_supysize": 1331,
}

CONSOLAS_BOLD: FontAttributes = {
    "em": 2048,
    "ascent": 1521,
    "descent": 527,
    # 下線
    "upos": -314,
    "uwidth": 194,
    # 取り消し線
    "os2_strikeypos": 512,
    "os2_strikeysize": 194,
    # 下付き文字
    "os2_subxoff": 0,
    "os2_subxsize": 1433,
    "os2_subyoff": 286,
    "os2_subysize": 1331,
    # 上付き文字
    "os2_supxoff": 0,
    "os2_supxsize": 1433,
    "os2_supyoff": 976,
    "os2_supysize": 1331,
}

HALF_WIDTH = 1126
FULL_ASCENT = 1884
FULL_DESCENT = 514


def set_font_attributes(
    target: fontforge.font, font_attributes: FontAttributes, *, is_bold: bool = False
):
    for k, v in font_attributes.items():
        setattr(target, k, v)

    # 組版時に使われるらしい。ascent, descent と揃える
    target.os2_typoascent = target.ascent
    target.os2_typodescent = -target.descent  # 負にする
    target.os2_use_typo_metrics = 0

    # target.os2_vendor # use default value "PfEd"
    target.os2_weight = 400 if not is_bold else 700  # Regular: 400, Bold: 700
    target.weight = "Book" if not is_bold else "Bold"  # Regular: "Book", Bold: "Bold"
    tmp = list(target.os2_panose)
    tmp[2] = 5 if not is_bold else 8  # Regular: 5, Bold: 8
    tmp[3] = 9  # monospaced
    target.os2_panose = tuple(tmp)

    # 余白を含む ascent
    target.hhea_ascent = FULL_ASCENT
    target.os2_winascent = target.hhea_ascent

    # 余白を含む descent
    target.os2_windescent = FULL_DESCENT
    target.hhea_descent = -target.os2_windescent  # 負にする

    target.hhea_linegap = 0
    target.os2_typolinegap = 0
    target.vhea_linegap = 0
    target.hhea_ascent_add = 0
    target.hhea_descent_add = 0
    target.os2_typoascent_add = 0
    target.os2_typodescent_add = 0
    target.os2_winascent_add = 0
    target.os2_windescent_add = 0


def generate_basefont(font_attributes: FontAttributes):
    f = fontforge.font()

    # デフォルトの ISO8859-1 から UnicodeFull に変更する
    f.reencode("UnicodeFull")

    set_font_attributes(f, font_attributes)

    f.version = "1.00"

    height = FULL_ASCENT + FULL_DESCENT
    overlap = math.ceil(height * 0.1 / 2)

    f.createChar(0x21)
    f[0x21].glyphname = fontforge.nameFromUnicode(0x21)

    f.hhea_ascent = FULL_ASCENT - 240
    f.os2_winascent = f.hhea_ascent
    f.os2_windescent = FULL_DESCENT - 240
    f.hhea_descent = -f.os2_windescent  # 負にする

    f[0x21].width = 1918
    f.familyname = "Full"
    f.fontname = "Full"
    f.fullname = "Full"
    f.generate("full.ttf", flags=("opentype"))

    f.hhea_ascent = FULL_ASCENT + overlap
    f.os2_winascent = f.hhea_ascent
    f.os2_windescent = FULL_DESCENT + overlap
    f.hhea_descent = -f.os2_windescent  # 負にする

    f[0x21].width = HALF_WIDTH
    f.familyname = "Half"
    f.fontname = "Half"
    f.fullname = "Half"
    f.generate("half.ttf", flags=("opentype"))


def set_borders(font: fontforge.font):
    border = fontforge.open("ReplaceParts.ttf")
    assert isinstance(border, fontforge.font)
    border.selection.select(("ranges", "unicode"), 0x2500, 0x257F)
    for g in list(border.selection.byGlyphs):
        uni = g.unicode
        border.selection.select(uni)
        border.copy()

        font.selection.select(uni)
        font.paste()
        font[uni].glyphname = fontforge.nameFromUnicode(uni)


def set_nerd_half(font: fontforge.font):
    nerd_half = fontforge.open("HalfNerdFontMono-Regular.ttf")
    assert isinstance(nerd_half, fontforge.font)
    nerd_half.removeGlyph(0x21)
    for gn in nerd_half:
        if (uni := nerd_half[gn].unicode) == -1:
            continue
        if (
            0x23FB <= uni <= 0x23FE
            or 0x2500 <= uni <= 0x259F
            or uni == 0x2B58
            or 0xE0A0 <= uni <= 0xE0D4
        ):
            nerd_half.selection.select(uni)
            nerd_half.copy()

            font.selection.select(uni)
            font.paste()
            font[uni].glyphname = fontforge.nameFromUnicode(uni)
            font[uni].width = HALF_WIDTH


def set_nerd_full(font: fontforge.font):
    nerd_full = fontforge.open("FullNerdFontMono-Regular.ttf")
    assert isinstance(nerd_full, fontforge.font)
    nerd_full.removeGlyph(0x21)

    trans_move = psMat.translate((167, 0))
    for gn in nerd_full:
        if (uni := nerd_full[gn].unicode) == -1:
            continue
        if not font.__contains__(uni):
            nerd_full.selection.select(uni)
            nerd_full.copy()

            font.selection.select(uni)
            font.paste()
            font[uni].glyphname = fontforge.nameFromUnicode(uni)
            font[uni].transform(trans_move)
            font[uni].width = HALF_WIDTH * 2


def set_nasum_font(font: fontforge.font, ttf_file: str):
    with open("exclude.json") as f:
        exclude = json.load(f)

    nasum = fontforge.open(ttf_file)
    assert isinstance(nasum, fontforge.font)
    nasum.selection.all()
    nasum.unlinkReferences()

    mag = 1.8
    trans_scale = psMat.scale(mag, mag)
    trans_moveH = psMat.translate(((HALF_WIDTH - 512 * mag) / 2, 0))
    trans_moveF = psMat.translate(((HALF_WIDTH * 2 - 1024 * mag) / 2, 0))
    for gn in nasum:
        if (uni := nasum[gn].unicode) == -1:
            continue
        if str(uni) not in exclude and not font.__contains__(uni):
            nasum.selection.select(uni)
            nasum.copy()

            font.selection.select(uni)
            font.paste()
            font[uni].glyphname = fontforge.nameFromUnicode(uni)

            if font[uni].width == 512:
                font[uni].transform(trans_scale)
                font[uni].transform(trans_moveH)
                font[uni].width = HALF_WIDTH
            elif font[uni].width == 1024:
                font[uni].transform(trans_scale)
                font[uni].transform(trans_moveF)
                font[uni].width = HALF_WIDTH * 2
    font.createChar(0x20)
    font[0x20].glyphname = fontforge.nameFromUnicode(0x20)
    font[0x20].width = HALF_WIDTH


def generate_regular():
    font = fontforge.font()

    # デフォルトの ISO8859-1 から UnicodeFull に変更する
    font.reencode("UnicodeFull")

    set_font_attributes(font, CONSOLAS_REGULAR)

    set_borders(font)

    set_nerd_half(font)

    set_nerd_full(font)

    set_nasum_font(font, "NasuFont20200227/NasuM-Regular-20200227.ttf")

    font.version = "1.00"

    # font.copyright # use default value
    font.familyname = "For Consolas"
    font.fontname = "ForConsolas-Regular"
    font.fullname = "For Consolas Regular"
    # font.sfntRevision # use automatic set value
    # font.sfnt_names # use automatic set value

    font.generate(f"{font.fontname}.ttf", flags=("opentype"))


def generate_bold():
    font = fontforge.font()

    # デフォルトの ISO8859-1 から UnicodeFull に変更する
    font.reencode("UnicodeFull")

    set_font_attributes(font, CONSOLAS_BOLD, is_bold=True)

    set_borders(font)

    set_nerd_half(font)

    set_nerd_full(font)

    set_nasum_font(font, "NasuFont20200227/NasuM-Bold-20200227.ttf")

    font.version = "1.00"

    # font.copyright # use default value
    font.familyname = "For Consolas"
    font.fontname = "ForConsolas-Bold"
    font.fullname = "For Consolas Bold"
    # font.sfntRevision # use automatic set value
    # font.sfnt_names # use automatic set value

    font.generate(f"{font.fontname}.ttf", flags=("opentype"))


def generate_inconsolata_regular():
    font = fontforge.font()

    # デフォルトの ISO8859-1 から UnicodeFull に変更する
    font.reencode("UnicodeFull")

    set_font_attributes(font, CONSOLAS_REGULAR)

    inconsolata = fontforge.open("Inconsolata-Regular.ttf")
    assert isinstance(inconsolata, fontforge.font)
    inconsolata.selection.all()
    inconsolata.unlinkReferences()

    trans_scale = psMat.scale(1024 / 500, 1024 / 500)
    trans_move = psMat.translate((51, 0))
    for gn in inconsolata:
        if (uni := inconsolata[gn].unicode) == -1:
            continue
        inconsolata.selection.select(uni)
        inconsolata.copy()

        font.selection.select(uni)
        font.paste()
        font[uni].glyphname = ".notdef" if uni == 0 else fontforge.nameFromUnicode(uni)

        if font[uni].width:
            font[uni].transform(trans_scale)
            font[uni].transform(trans_move)
            font[uni].width = 1126

    font.version = "1.00"

    # font.copyright # use default value
    font.familyname = "My Inconsolata"
    font.fontname = "MyInconsolata-Regular"
    font.fullname = "My Inconsolata Regular"
    # font.sfntRevision # use automatic set value
    # font.sfnt_names # use automatic set value

    font.generate(f"{font.fontname}.ttf", flags=("opentype"))


def generate_inconsolata_bold():
    font = fontforge.font()

    # デフォルトの ISO8859-1 から UnicodeFull に変更する
    font.reencode("UnicodeFull")

    set_font_attributes(font, CONSOLAS_BOLD, is_bold=True)

    inconsolata = fontforge.open("Inconsolata-Bold.ttf")
    assert isinstance(inconsolata, fontforge.font)
    inconsolata.selection.all()
    inconsolata.unlinkReferences()

    trans_move = psMat.translate((51, 0))
    for gn in inconsolata:
        if (uni := inconsolata[gn].unicode) == -1:
            continue
        inconsolata.selection.select(uni)
        inconsolata.copy()

        font.selection.select(uni)
        font.paste()
        font[uni].glyphname = ".notdef" if uni == 0 else fontforge.nameFromUnicode(uni)

        if font[uni].width:
            font[uni].transform(trans_move)
            font[uni].width = 1126

    font.version = "1.00"

    # font.copyright # use default value
    font.familyname = "My Inconsolata"
    font.fontname = "MyInconsolata-Bold"
    font.fullname = "My Inconsolata Bold"
    # font.sfntRevision # use automatic set value
    # font.sfnt_names # use automatic set value

    font.generate(f"{font.fontname}.ttf", flags=("opentype"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--generate", choices=["regular", "bold", "inconsolata"])
    args = parser.parse_args()

    if args.prepare:
        generate_basefont(CONSOLAS_REGULAR)
    elif args.generate == "regular":
        generate_regular()
    elif args.generate == "bold":
        generate_bold()
    elif args.generate == "inconsolata":
        generate_inconsolata_regular()
        generate_inconsolata_bold()


if __name__ == "__main__":
    main()
