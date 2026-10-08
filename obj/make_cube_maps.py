#!/usr/bin/env python3
"""
Generate cube texture + normal PNG atlases in obj/.
No external dependencies (uses only Python stdlib).

Outputs:
- cube_tx.png
- cube_normal.png
"""

import math
import os
import struct
import zlib


OUT_DIR = os.path.dirname(os.path.abspath(__file__))
TX_PATH = os.path.join(OUT_DIR, "cube_tx.png")
NM_PATH = os.path.join(OUT_DIR, "cube_normal.png")

SIZE = 1024
CELL = SIZE // 4
BORDER = 10
GRID_THICK = 3


def clamp8(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)


def write_png_rgb(path, width, height, rgb_rows):
    # rgb_rows: iterable of bytes, each row length = width*3
    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = bytearray()
    for row in rgb_rows:
        raw.append(0)  # filter type 0
        raw.extend(row)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # RGB
    idat = zlib.compress(bytes(raw), level=9)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", idat))
        f.write(chunk(b"IEND", b""))


def face_color(face_x, face_y):
    # 4x4 UV test-grid palette with broad hue variation
    h = (face_x * 0.21 + face_y * 0.13) % 1.0
    s = 0.68
    v = 0.92

    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)

    i = i % 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return int(r * 255), int(g * 255), int(b * 255)


def make_texture_rows():
    rows = []
    cx = SIZE / 2
    cy = SIZE / 2
    max_r = math.hypot(cx, cy)

    for y in range(SIZE):
        row = bytearray()
        for x in range(SIZE):
            fx = x // CELL
            fy = y // CELL
            lx = x % CELL
            ly = y % CELL

            base_r, base_g, base_b = face_color(fx, fy)

            # global radial shading for visual interest
            rr = math.hypot(x - cx, y - cy) / max_r
            shade = 1.0 - 0.22 * rr

            r = clamp8(base_r * shade)
            g = clamp8(base_g * shade)
            b = clamp8(base_b * shade)

            # thick face border for UV edges
            near_border = (
                lx < BORDER or ly < BORDER or
                lx >= CELL - BORDER or ly >= CELL - BORDER
            )
            if near_border:
                r, g, b = 8, 8, 8

            # inner border ring to make edges pop
            inner = BORDER + 16
            near_inner = (
                lx < inner or ly < inner or
                lx >= CELL - inner or ly >= CELL - inner
            )
            if near_inner and not near_border:
                r, g, b = 240, 240, 240

            # local checker in each cell
            checker = ((lx // 24) + (ly // 24)) % 2
            if checker == 0:
                r = clamp8(r * 0.92)
                g = clamp8(g * 0.92)
                b = clamp8(b * 0.92)
            else:
                r = clamp8(r * 1.06)
                g = clamp8(g * 1.06)
                b = clamp8(b * 1.06)

            # crosshair + diagonals per face for orientation
            if abs(lx - CELL // 2) < GRID_THICK or abs(ly - CELL // 2) < GRID_THICK:
                r, g, b = 255, 255, 255
            if abs((lx - ly)) < GRID_THICK or abs((lx + ly) - (CELL - 1)) < GRID_THICK:
                r, g, b = 0, 0, 0

            # global atlas grid lines between faces
            if x % CELL < GRID_THICK or y % CELL < GRID_THICK:
                r, g, b = 255, 255, 255

            row.extend((r, g, b))
        rows.append(bytes(row))
    return rows


def make_normal_rows():
    rows = []
    for y in range(SIZE):
        row = bytearray()
        for x in range(SIZE):
            lx = x % CELL
            ly = y % CELL

            # flat tangent-space normal base
            nx, ny, nz = 0.0, 0.0, 1.0

            # emboss near face borders so UV islands are obvious
            dist_edge = min(lx, ly, CELL - 1 - lx, CELL - 1 - ly)
            if dist_edge < 18:
                # push outward from nearest edge
                if lx == dist_edge:
                    nx += 0.55
                if ly == dist_edge:
                    ny += 0.55
                if (CELL - 1 - lx) == dist_edge:
                    nx -= 0.55
                if (CELL - 1 - ly) == dist_edge:
                    ny -= 0.55

            # normalize
            length = math.sqrt(nx * nx + ny * ny + nz * nz)
            nx /= length
            ny /= length
            nz /= length

            r = clamp8((nx * 0.5 + 0.5) * 255)
            g = clamp8((ny * 0.5 + 0.5) * 255)
            b = clamp8((nz * 0.5 + 0.5) * 255)

            row.extend((r, g, b))
        rows.append(bytes(row))
    return rows


def main():
    tx_rows = make_texture_rows()
    nm_rows = make_normal_rows()
    write_png_rgb(TX_PATH, SIZE, SIZE, tx_rows)
    write_png_rgb(NM_PATH, SIZE, SIZE, nm_rows)

    print(f"Wrote {os.path.basename(TX_PATH)}")
    print(f"Wrote {os.path.basename(NM_PATH)}")


if __name__ == "__main__":
    main()
