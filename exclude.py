#!/usr/bin/env python3
# pyright: reportUnknownMemberType=false
from __future__ import annotations

import json
from unicodedata import category, east_asian_width

import fontforge

CONSOLAS_PATH = ""


def main():
    consolas = fontforge.open(CONSOLAS_PATH)
    assert isinstance(consolas, fontforge.font)

    list: list[int] = []
    for gn in consolas:
        if (uni := consolas[gn].unicode) == -1:
            continue
        # Consolas には Fullwidth, Wide な文字は含まれない
        # Consolas に含まれる East Asian Width が Ambiguous かつカテゴリが Letter の文字
        if (eaw := east_asian_width(chr(uni))) in ["H", "Na", "N"] or (
            eaw == "A" and category(chr(uni))[0] in ["L"]
        ):
            list.append(uni)
    exclude = {k: True for k in sorted(list)}

    print(json.dumps(exclude))


if __name__ == "__main__":
    main()
