#!/usr/bin/fontforge -script
import math
import fontforge
import psMat

em = 2048
width = 1126
_ascent = 1521
_descent = 527
ascent = 1884
descent = 514
height = ascent + descent
gap = math.ceil(height * 0.1 / 2)
ascent += gap
descent += gap

bl = 0
br = width
bw = br - bl
cx = (bl + br) / 2.0
bb = -descent
bt = ascent
bh = bt - bb
cy = (bb + bt) / 2.0
swl2 = 72 / 2.0 * 2
swh2 = 146 / 2.0 * 2
dg2 = 118 / 2.0 * 2
dd = dg2 + 2 * swl2

xrefT = psMat.compose(psMat.translate(-2 * cx, 0), psMat.scale(-1, 1))
yrefT = psMat.compose(psMat.translate(0, -2 * cy), psMat.scale(1, -1))

def addchar(font, cp, contours):
    glyph = font.createChar(cp, 'uni{:04X}'.format(cp))
    pen = glyph.glyphPen()
    for c in contours:
        c.draw(pen)
    pen = None
    glyph.removeOverlap()
    glyph.simplify(1, ('forcelines',))
    glyph.round()
    glyph.correctDirection()
    glyph.canonicalStart()
    glyph.canonicalContours()
    glyph.width = width

def rect(left, bottom, right, top):
    c = fontforge.contour()
    c.moveTo(left, bottom)
    c.lineTo(left, top)
    c.lineTo(right, top)
    c.lineTo(right, bottom)
    c.closed = True
    return c

def frange(start, stop, step):
    while start < stop:
        yield start
        start += step


font = fontforge.font()
font.familyname = 'ReplaceParts'
font.fontname = font.familyname
font.fullname = font.familyname
font.weight = 'Regular'
font.em = em
font.ascent = _ascent
font.descent = _descent
font.os2_winascent = ascent
font.os2_winascent_add = 0
font.os2_windescent = descent
font.os2_windescent_add = 0
font.os2_typoascent = _ascent
font.os2_typoascent_add = 0
font.os2_typodescent = -_descent
font.os2_typodescent_add = 0
font.os2_typolinegap = 0
font.hhea_ascent = ascent
font.hhea_ascent_add = 0
font.hhea_descent = -descent
font.hhea_descent_add = 0
font.hhea_linegap = 0

# Box drawing characters
NONE   = 0
LIGHT  = 1
HEAVY  = 2
DOUBLE = 3

def boxdrawing_sbound(l, r, o):
    if l == NONE and r == NONE:
        return 0
    elif l == DOUBLE and r == DOUBLE and o == NONE:
        return -dg2
    elif l == DOUBLE or r == DOUBLE:
        return dd
    elif l == HEAVY or r == HEAVY:
        return swh2
    else:
        return swl2

def boxdrawing_dbound(l, r):
    if l == NONE and r == NONE:
        return (0, 0)
    elif l == DOUBLE and r == DOUBLE:
        return (-dg2, -dg2)
    elif l == DOUBLE and r == NONE:
        return (-dg2, dd)
    elif l == NONE and r == DOUBLE:
        return (dd, -dg2)
    else:
        return (swl2, swl2)

def boxdrawing(left, top, right, bottom):
    contours = []

    if left == LIGHT or left == HEAVY:
        bound = cx + boxdrawing_sbound(top, bottom, right)
        if left == LIGHT:
            contours.append(rect(bl, cy - swl2, bound, cy + swl2))
        else:
            contours.append(rect(bl, cy - swh2, bound, cy + swh2))
    elif left == DOUBLE:
        bound1, bound2 = (cx + x for x in boxdrawing_dbound(top, bottom))
        contours.append(rect(bl, cy + dg2, bound1, cy + dd))
        contours.append(rect(bl, cy - dd, bound2, cy - dg2))

    if top == LIGHT or top == HEAVY:
        bound = cy - boxdrawing_sbound(right, left, bottom)
        if top == LIGHT:
            contours.append(rect(cx - swl2, bound, cx + swl2, bt))
        else:
            contours.append(rect(cx - swh2, bound, cx + swh2, bt))
    elif top == DOUBLE:
        bound1, bound2 = (cy - x for x in boxdrawing_dbound(right, left))
        contours.append(rect(cx + dg2, bound1, cx + dd, bt))
        contours.append(rect(cx - dd, bound2, cx - dg2, bt))

    if right == LIGHT or right == HEAVY:
        bound = cx - boxdrawing_sbound(bottom, top, left)
        if right == LIGHT:
            contours.append(rect(bound, cy - swl2, br, cy + swl2))
        else:
            contours.append(rect(bound, cy - swh2, br, cy + swh2))
    elif right == DOUBLE:
        bound1, bound2 = (cx - x for x in boxdrawing_dbound(bottom, top))
        contours.append(rect(bound1, cy - dd, br, cy - dg2))
        contours.append(rect(bound2, cy + dg2, br, cy + dd))

    if bottom == LIGHT or bottom == HEAVY:
        bound = cy + boxdrawing_sbound(left, right, top)
        if bottom == LIGHT:
            contours.append(rect(cx - swl2, bb, cx + swl2, bound))
        else:
            contours.append(rect(cx - swh2, bb, cx + swh2, bound))
    elif bottom == DOUBLE:
        bound1, bound2 = (cy + x for x in boxdrawing_dbound(left, right))
        contours.append(rect(cx - dd, bb, cx - dg2, bound1))
        contours.append(rect(cx + dg2, bb, cx + dd, bound2))

    return contours

def boxdrawing_hdash(number, weight):
    s = float(bw) / number
    dl = s / 2.0
    sw2 = swl2 if weight == LIGHT else swh2
    return [rect(l, cy - sw2, l + dl, cy + sw2)
            for l in frange(bl + s / 4.0, br, s)]

def boxdrawing_vdash(number, weight):
    s = float(bh) / number
    dl = s / 2.0
    sw2 = swl2 if weight == LIGHT else swh2
    return [rect(cx - sw2, b, cx + sw2, b + dl)
            for b in frange(bb + s / 4.0, bt, s)]

def boxdrawing_arc(xref=False, yref=False):
    K = 0.5522847498
    r = min(bw, bh) / 2.0
    Ci = K * (r - swl2) - r
    Co = K * (r + swl2) - r

    c = fontforge.contour()
    c.moveTo(bl, cy + swl2)
    c.lineTo(cx - r, cy + swl2)
    c.cubicTo((cx + Ci, cy + swl2),
              (cx - swl2, cy - Ci),
              (cx - swl2, cy + r))
    c.lineTo(cx - swl2, bt)
    c.lineTo(cx + swl2, bt)
    c.lineTo(cx + swl2, cy + r)
    c.cubicTo((cx + swl2, cy - Co),
              (cx + Co, cy - swl2),
              (cx - r, cy - swl2))
    c.lineTo(bl, cy - swl2)
    c.closed = True

    if xref:
        c.transform(xrefT)
    if yref:
        c.transform(yrefT)
    return [c]

def boxdrawing_diagonal(up=True, down=True):
    t = math.atan2(bh, bw)
    dx = swl2 / math.sin(t)
    dy = swl2 / math.cos(t)
    contours = []
    if up:
        c = fontforge.contour()
        c.moveTo(bl, bb)
        c.lineTo(bl, bb + dy)
        c.lineTo(br - dx, bt)
        c.lineTo(br, bt)
        c.lineTo(br, bt - dy)
        c.lineTo(bl + dx, bb)
        c.closed = True
        contours.append(c)
    if down:
        c = fontforge.contour()
        c.moveTo(bl, bt)
        c.lineTo(bl + dx, bt)
        c.lineTo(br, bb + dy)
        c.lineTo(br, bb)
        c.lineTo(br - dx, bb)
        c.lineTo(bl, bt - dy)
        c.closed = True
        contours.append(c)
    return contours

addchar(font, 0x2500, boxdrawing(LIGHT, NONE,  LIGHT, NONE))
addchar(font, 0x2501, boxdrawing(HEAVY, NONE,  HEAVY, NONE))
addchar(font, 0x2502, boxdrawing(NONE,  LIGHT, NONE,  LIGHT))
addchar(font, 0x2503, boxdrawing(NONE,  HEAVY, NONE,  HEAVY))
addchar(font, 0x2504, boxdrawing_hdash(3, LIGHT))
addchar(font, 0x2505, boxdrawing_hdash(3, HEAVY))
addchar(font, 0x2506, boxdrawing_vdash(3, LIGHT))
addchar(font, 0x2507, boxdrawing_vdash(3, HEAVY))
addchar(font, 0x2508, boxdrawing_hdash(4, LIGHT))
addchar(font, 0x2509, boxdrawing_hdash(4, HEAVY))
addchar(font, 0x250A, boxdrawing_vdash(4, LIGHT))
addchar(font, 0x250B, boxdrawing_vdash(4, HEAVY))
addchar(font, 0x250C, boxdrawing(NONE,  NONE,  LIGHT, LIGHT))
addchar(font, 0x250D, boxdrawing(NONE,  NONE,  HEAVY, LIGHT))
addchar(font, 0x250E, boxdrawing(NONE,  NONE,  LIGHT, HEAVY))
addchar(font, 0x250F, boxdrawing(NONE,  NONE,  HEAVY, HEAVY))
addchar(font, 0x2510, boxdrawing(LIGHT, NONE,  NONE,  LIGHT))
addchar(font, 0x2511, boxdrawing(HEAVY, NONE,  NONE,  LIGHT))
addchar(font, 0x2512, boxdrawing(LIGHT, NONE,  NONE,  HEAVY))
addchar(font, 0x2513, boxdrawing(HEAVY, NONE,  NONE,  HEAVY))
addchar(font, 0x2514, boxdrawing(NONE,  LIGHT, LIGHT, NONE))
addchar(font, 0x2515, boxdrawing(NONE,  LIGHT, HEAVY, NONE))
addchar(font, 0x2516, boxdrawing(NONE,  HEAVY, LIGHT, NONE))
addchar(font, 0x2517, boxdrawing(NONE,  HEAVY, HEAVY, NONE))
addchar(font, 0x2518, boxdrawing(LIGHT, LIGHT, NONE,  NONE))
addchar(font, 0x2519, boxdrawing(HEAVY, LIGHT, NONE,  NONE))
addchar(font, 0x251A, boxdrawing(LIGHT, HEAVY, NONE,  NONE))
addchar(font, 0x251B, boxdrawing(HEAVY, HEAVY, NONE,  NONE))
addchar(font, 0x251C, boxdrawing(NONE,  LIGHT, LIGHT, LIGHT))
addchar(font, 0x251D, boxdrawing(NONE,  LIGHT, HEAVY, LIGHT))
addchar(font, 0x251E, boxdrawing(NONE,  HEAVY, LIGHT, LIGHT))
addchar(font, 0x251F, boxdrawing(NONE,  LIGHT, LIGHT, HEAVY))
addchar(font, 0x2520, boxdrawing(NONE,  HEAVY, LIGHT, HEAVY))
addchar(font, 0x2521, boxdrawing(NONE,  HEAVY, HEAVY, LIGHT))
addchar(font, 0x2522, boxdrawing(NONE,  LIGHT, HEAVY, HEAVY))
addchar(font, 0x2523, boxdrawing(NONE,  HEAVY, HEAVY, HEAVY))
addchar(font, 0x2524, boxdrawing(LIGHT, LIGHT, NONE,  LIGHT))
addchar(font, 0x2525, boxdrawing(HEAVY, LIGHT, NONE,  LIGHT))
addchar(font, 0x2526, boxdrawing(LIGHT, HEAVY, NONE,  LIGHT))
addchar(font, 0x2527, boxdrawing(LIGHT, LIGHT, NONE,  HEAVY))
addchar(font, 0x2528, boxdrawing(LIGHT, HEAVY, NONE,  HEAVY))
addchar(font, 0x2529, boxdrawing(HEAVY, HEAVY, NONE,  LIGHT))
addchar(font, 0x252A, boxdrawing(HEAVY, LIGHT, NONE,  HEAVY))
addchar(font, 0x252B, boxdrawing(HEAVY, HEAVY, NONE,  HEAVY))
addchar(font, 0x252C, boxdrawing(LIGHT, NONE,  LIGHT, LIGHT))
addchar(font, 0x252D, boxdrawing(HEAVY, NONE,  LIGHT, LIGHT))
addchar(font, 0x252E, boxdrawing(LIGHT, NONE,  HEAVY, LIGHT))
addchar(font, 0x252F, boxdrawing(HEAVY, NONE,  HEAVY, LIGHT))
addchar(font, 0x2530, boxdrawing(LIGHT, NONE,  LIGHT, HEAVY))
addchar(font, 0x2531, boxdrawing(HEAVY, NONE,  LIGHT, HEAVY))
addchar(font, 0x2532, boxdrawing(LIGHT, NONE,  HEAVY, HEAVY))
addchar(font, 0x2533, boxdrawing(HEAVY, NONE,  HEAVY, HEAVY))
addchar(font, 0x2534, boxdrawing(LIGHT, LIGHT, LIGHT, NONE))
addchar(font, 0x2535, boxdrawing(HEAVY, LIGHT, LIGHT, NONE))
addchar(font, 0x2536, boxdrawing(LIGHT, LIGHT, HEAVY, NONE))
addchar(font, 0x2537, boxdrawing(HEAVY, LIGHT, HEAVY, NONE))
addchar(font, 0x2538, boxdrawing(LIGHT, HEAVY, LIGHT, NONE))
addchar(font, 0x2539, boxdrawing(HEAVY, HEAVY, LIGHT, NONE))
addchar(font, 0x253A, boxdrawing(LIGHT, HEAVY, HEAVY, NONE))
addchar(font, 0x253B, boxdrawing(HEAVY, HEAVY, HEAVY, NONE))
addchar(font, 0x253C, boxdrawing(LIGHT, LIGHT, LIGHT, LIGHT))
addchar(font, 0x253D, boxdrawing(HEAVY, LIGHT, LIGHT, LIGHT))
addchar(font, 0x253E, boxdrawing(LIGHT, LIGHT, HEAVY, LIGHT))
addchar(font, 0x253F, boxdrawing(HEAVY, LIGHT, HEAVY, LIGHT))
addchar(font, 0x2540, boxdrawing(LIGHT, HEAVY, LIGHT, LIGHT))
addchar(font, 0x2541, boxdrawing(LIGHT, LIGHT, LIGHT, HEAVY))
addchar(font, 0x2542, boxdrawing(LIGHT, HEAVY, LIGHT, HEAVY))
addchar(font, 0x2543, boxdrawing(HEAVY, HEAVY, LIGHT, LIGHT))
addchar(font, 0x2544, boxdrawing(LIGHT, HEAVY, HEAVY, LIGHT))
addchar(font, 0x2545, boxdrawing(HEAVY, LIGHT, LIGHT, HEAVY))
addchar(font, 0x2546, boxdrawing(LIGHT, LIGHT, HEAVY, HEAVY))
addchar(font, 0x2547, boxdrawing(HEAVY, HEAVY, HEAVY, LIGHT))
addchar(font, 0x2548, boxdrawing(HEAVY, LIGHT, HEAVY, HEAVY))
addchar(font, 0x2549, boxdrawing(HEAVY, HEAVY, LIGHT, HEAVY))
addchar(font, 0x254A, boxdrawing(LIGHT, HEAVY, HEAVY, HEAVY))
addchar(font, 0x254B, boxdrawing(HEAVY, HEAVY, HEAVY, HEAVY))
addchar(font, 0x254C, boxdrawing_hdash(2, LIGHT))
addchar(font, 0x254D, boxdrawing_hdash(2, HEAVY))
addchar(font, 0x254E, boxdrawing_vdash(2, LIGHT))
addchar(font, 0x254F, boxdrawing_vdash(2, HEAVY))
addchar(font, 0x2550, boxdrawing(DOUBLE, NONE,   DOUBLE, NONE))
addchar(font, 0x2551, boxdrawing(NONE,   DOUBLE, NONE,   DOUBLE))
addchar(font, 0x2552, boxdrawing(NONE,   NONE,   DOUBLE, LIGHT))
addchar(font, 0x2553, boxdrawing(NONE,   NONE,   LIGHT,  DOUBLE))
addchar(font, 0x2554, boxdrawing(NONE,   NONE,   DOUBLE, DOUBLE))
addchar(font, 0x2555, boxdrawing(DOUBLE, NONE,   NONE,   LIGHT))
addchar(font, 0x2556, boxdrawing(LIGHT,  NONE,   NONE,   DOUBLE))
addchar(font, 0x2557, boxdrawing(DOUBLE, NONE,   NONE,   DOUBLE))
addchar(font, 0x2558, boxdrawing(NONE,   LIGHT,  DOUBLE, NONE))
addchar(font, 0x2559, boxdrawing(NONE,   DOUBLE, LIGHT,  NONE))
addchar(font, 0x255A, boxdrawing(NONE,   DOUBLE, DOUBLE, NONE))
addchar(font, 0x255B, boxdrawing(DOUBLE, LIGHT,  NONE,   NONE))
addchar(font, 0x255C, boxdrawing(LIGHT,  DOUBLE, NONE,   NONE))
addchar(font, 0x255D, boxdrawing(DOUBLE, DOUBLE, NONE,   NONE))
addchar(font, 0x255E, boxdrawing(NONE,   LIGHT,  DOUBLE, LIGHT))
addchar(font, 0x255F, boxdrawing(NONE,   DOUBLE, LIGHT,  DOUBLE))
addchar(font, 0x2560, boxdrawing(NONE,   DOUBLE, DOUBLE, DOUBLE))
addchar(font, 0x2561, boxdrawing(DOUBLE, LIGHT,  NONE,   LIGHT))
addchar(font, 0x2562, boxdrawing(LIGHT,  DOUBLE, NONE,   DOUBLE))
addchar(font, 0x2563, boxdrawing(DOUBLE, DOUBLE, NONE,   DOUBLE))
addchar(font, 0x2564, boxdrawing(DOUBLE, NONE,   DOUBLE, LIGHT))
addchar(font, 0x2565, boxdrawing(LIGHT,  NONE,   LIGHT,  DOUBLE))
addchar(font, 0x2566, boxdrawing(DOUBLE, NONE,   DOUBLE, DOUBLE))
addchar(font, 0x2567, boxdrawing(DOUBLE, LIGHT,  DOUBLE, NONE))
addchar(font, 0x2568, boxdrawing(LIGHT,  DOUBLE, LIGHT,  NONE))
addchar(font, 0x2569, boxdrawing(DOUBLE, DOUBLE, DOUBLE, NONE))
addchar(font, 0x256A, boxdrawing(DOUBLE, LIGHT,  DOUBLE, LIGHT))
addchar(font, 0x256B, boxdrawing(LIGHT,  DOUBLE, LIGHT,  DOUBLE))
addchar(font, 0x256C, boxdrawing(DOUBLE, DOUBLE, DOUBLE, DOUBLE))
addchar(font, 0x256D, boxdrawing_arc(True,  True))
addchar(font, 0x256E, boxdrawing_arc(False, True))
addchar(font, 0x256F, boxdrawing_arc(False, False))
addchar(font, 0x2570, boxdrawing_arc(True,  False))
addchar(font, 0x2571, boxdrawing_diagonal(True,  False))
addchar(font, 0x2572, boxdrawing_diagonal(False, True))
addchar(font, 0x2573, boxdrawing_diagonal(True,  True))
addchar(font, 0x2574, boxdrawing(LIGHT, NONE,  NONE,  NONE))
addchar(font, 0x2575, boxdrawing(NONE,  LIGHT, NONE,  NONE))
addchar(font, 0x2576, boxdrawing(NONE,  NONE,  LIGHT, NONE))
addchar(font, 0x2577, boxdrawing(NONE,  NONE,  NONE,  LIGHT))
addchar(font, 0x2578, boxdrawing(HEAVY, NONE,  NONE,  NONE))
addchar(font, 0x2579, boxdrawing(NONE,  HEAVY, NONE,  NONE))
addchar(font, 0x257A, boxdrawing(NONE,  NONE,  HEAVY, NONE))
addchar(font, 0x257B, boxdrawing(NONE,  NONE,  NONE,  HEAVY))
addchar(font, 0x257C, boxdrawing(LIGHT, NONE,  HEAVY, NONE))
addchar(font, 0x257D, boxdrawing(NONE,  LIGHT, NONE,  HEAVY))
addchar(font, 0x257E, boxdrawing(HEAVY, NONE,  LIGHT, NONE))
addchar(font, 0x257F, boxdrawing(NONE,  HEAVY, NONE,  LIGHT))

# Block Elements
def block_shade(darkness):
    vs = bh / 8.0
    hs = bw / 4.0
    if darkness == 'light':
        m1 = (1, 0, 0, 0)
        m2 = (0, 0, 1, 0)
    elif darkness == 'medium':
        m1 = (1, 0, 0, 1)
        m2 = (1, 0, 0, 1)
    else:
        m1 = (0, 1, 1, 1)
        m2 = (1, 1, 0, 1)

    contours = []
    for l, m in [(bl, m1), (bl + 2 * hs, m2)]:
        for b in frange(bb, bt, 2 * vs):
            if m[0]:
                contours.append(rect(l, b + vs, l + hs, b + 2 * vs))
            if m[1]:
                contours.append(rect(l + hs, b + vs, l + 2 * hs, b + 2 * vs))
            if m[2]:
                contours.append(rect(l, b, l + hs, b + vs))
            if m[3]:
                contours.append(rect(l + hs, b, l + 2 * hs, b + vs))
    return contours

def block_quadrant(ul, ur, ll, lr):
    contours = []
    if ul:
        contours.append(rect(bl, cy, cx, bt))
    if ur:
        contours.append(rect(cx, cy, br, bt))
    if ll:
        contours.append(rect(bl, bb, cx, cy))
    if lr:
        contours.append(rect(cx, bb, br, cy))
    return contours

addchar(font, 0x2580, [rect(bl, cy, br, bt)])
addchar(font, 0x2581, [rect(bl, bb, br, bb + bh * 1.0/8.0)])
addchar(font, 0x2582, [rect(bl, bb, br, bb + bh * 2.0/8.0)])
addchar(font, 0x2583, [rect(bl, bb, br, bb + bh * 3.0/8.0)])
addchar(font, 0x2584, [rect(bl, bb, br, bb + bh * 4.0/8.0)])
addchar(font, 0x2585, [rect(bl, bb, br, bb + bh * 5.0/8.0)])
addchar(font, 0x2586, [rect(bl, bb, br, bb + bh * 6.0/8.0)])
addchar(font, 0x2587, [rect(bl, bb, br, bb + bh * 7.0/8.0)])
addchar(font, 0x2588, [rect(bl, bb, br, bb + bh * 8.0/8.0)])
addchar(font, 0x2589, [rect(bl, bb, bl + bw * 7.0/8.0, bt)])
addchar(font, 0x258A, [rect(bl, bb, bl + bw * 6.0/8.0, bt)])
addchar(font, 0x258B, [rect(bl, bb, bl + bw * 5.0/8.0, bt)])
addchar(font, 0x258C, [rect(bl, bb, bl + bw * 4.0/8.0, bt)])
addchar(font, 0x258D, [rect(bl, bb, bl + bw * 3.0/8.0, bt)])
addchar(font, 0x258E, [rect(bl, bb, bl + bw * 2.0/8.0, bt)])
addchar(font, 0x258F, [rect(bl, bb, bl + bw * 1.0/8.0, bt)])
addchar(font, 0x2590, [rect(cx, bb, br, bt)])
addchar(font, 0x2591, block_shade('light'))
addchar(font, 0x2592, block_shade('medium'))
addchar(font, 0x2593, block_shade('dark'))
addchar(font, 0x2594, [rect(bl, bt - bh * 1.0/8.0, br, bt)])
addchar(font, 0x2595, [rect(br - bw * 1.0/8.0, bb, br, bt)])
addchar(font, 0x2596, block_quadrant(False, False, True,  False))
addchar(font, 0x2597, block_quadrant(False, False, False, True))
addchar(font, 0x2598, block_quadrant(True,  False, False, False))
addchar(font, 0x2599, block_quadrant(True,  False, True,  True))
addchar(font, 0x259A, block_quadrant(True,  False, False, True))
addchar(font, 0x259B, block_quadrant(True,  True,  True,  False))
addchar(font, 0x259C, block_quadrant(True,  True,  False, True))
addchar(font, 0x259D, block_quadrant(False, True,  False, False))
addchar(font, 0x259E, block_quadrant(False, True,  True,  False))
addchar(font, 0x259F, block_quadrant(False, True,  True,  True))

# Geometric Shapes
def geometric_triangle(rotation=0, black=True):
    sw = 46
    xm = 37
    b = bb + (bh - bw + 2 * xm) / 2.0
    t = b + (bw - 2 * xm) * math.sin(math.pi / 3)
    contours = []

    c = fontforge.contour()
    c.moveTo(bl + xm, b)
    c.lineTo(cx, t)
    c.lineTo(br - xm, b)
    c.closed = True
    contours.append(c)

    if not black:
        xm += sw * math.sqrt(3)
        c = fontforge.contour()
        c.moveTo(bl + xm, b + sw)
        c.lineTo(br - xm, b + sw)
        c.lineTo(cx, t - 2 * sw)
        c.closed = True
        contours.append(c)

    if rotation:
        cy = (b + t) / 2.0
        rotT = psMat.compose(psMat.translate(-cx, -cy),
               psMat.compose(psMat.rotate(rotation),
                             psMat.translate(cx, cy)))
        for c in contours:
            c.transform(rotT)
    return contours

addchar(font, 0x25B4, geometric_triangle(0, True))
addchar(font, 0x25B5, geometric_triangle(0, False))
addchar(font, 0x25B8, geometric_triangle(-math.pi / 2, True))
addchar(font, 0x25B9, geometric_triangle(-math.pi / 2, False))
addchar(font, 0x25BE, geometric_triangle(math.pi, True))
addchar(font, 0x25BF, geometric_triangle(math.pi, False))
addchar(font, 0x25C2, geometric_triangle(math.pi / 2, True))
addchar(font, 0x25C3, geometric_triangle(math.pi / 2, False))

# Braille Patterns
def braille_pattern(number):
    vs = bh / 8.0
    hs = bw / 4.0
    ls = list(frange(bl + hs / 2.0, br, 2 * hs))
    bs = list(frange(bb + vs / 2.0, bt, 2 * vs))
    contours = []

    if number & 1:
        contours.append(rect(ls[0], bs[3], ls[0] + hs, bs[3] + vs))
    if number & 2:
        contours.append(rect(ls[0], bs[2], ls[0] + hs, bs[2] + vs))
    if number & 4:
        contours.append(rect(ls[0], bs[1], ls[0] + hs, bs[1] + vs))
    if number & 8:
        contours.append(rect(ls[1], bs[3], ls[1] + hs, bs[3] + vs))
    if number & 16:
        contours.append(rect(ls[1], bs[2], ls[1] + hs, bs[2] + vs))
    if number & 32:
        contours.append(rect(ls[1], bs[1], ls[1] + hs, bs[1] + vs))
    if number & 64:
        contours.append(rect(ls[0], bs[0], ls[0] + hs, bs[0] + vs))
    if number & 128:
        contours.append(rect(ls[1], bs[0], ls[1] + hs, bs[0] + vs))
    return contours

for n in range(256):
    addchar(font, 0x2800 + n, braille_pattern(n))

# Powerline Symbols
def powerline_triangle(xref=False):
    c = fontforge.contour()
    c.moveTo(bl, bt)
    c.lineTo(br, cy)
    c.lineTo(bl, bb)
    c.closed = True
    if xref:
        c.transform(xrefT)
    return [c]

def powerline_angle(xref=False):
    t = math.atan2(cy - bb, bw)
    dx = swl2 / math.sin(t)
    dy = swl2 / math.cos(t)

    c = fontforge.contour()
    c.moveTo(bl, bt)
    c.lineTo(bl + dx, bt)
    c.lineTo(br, cy + dy)
    c.lineTo(br, cy - dy)
    c.lineTo(bl + dx, bb)
    c.lineTo(bl, bb)
    c.lineTo(bl, bb + dy)
    c.lineTo(br - dx, cy)
    c.lineTo(bl, bt - dy)
    c.closed = True
    if xref:
        c.transform(xrefT)
    return [c]

addchar(font, 0xE0B0, powerline_triangle(False))
addchar(font, 0xE0B1, powerline_angle(False))
addchar(font, 0xE0B2, powerline_triangle(True))
addchar(font, 0xE0B3, powerline_angle(True))

font.generate('ReplaceParts.ttf', '', ('opentype', 'PfEd-lookups', 'TeX-table'))
