import math

w = 10.0
h = 8.0
t = 1.0
half = w / 2.0
length = math.hypot(half, h)
ux = half / length
uy = h / length
nx = -uy
ny = ux
offset = t / 2.0
lx0, ly0 = -half, 0.0
lx1, ly1 = 0.0, h
left_rect = [
    (lx0 + nx * offset, ly0 + ny * offset),
    (lx0 - nx * offset, ly0 - ny * offset),
    (lx1 - nx * offset, ly1 - ny * offset),
    (lx1 + nx * offset, ly1 + ny * offset),
]
rx0, ry0 = half, 0.0
rx1, ry1 = 0.0, h
right_rect = [
    (rx0 - nx * offset, ry0 - ny * offset),
    (rx0 + nx * offset, ry0 + ny * offset),
    (rx1 + nx * offset, ry1 + ny * offset),
    (rx1 - nx * offset, ry1 - ny * offset),
]
print("left", left_rect)
print("right", right_rect)

# Try to build polygon by tracing left outer edge (left_rect[0])->left_rect[1]??
# Let's inspect points
pts = [
    left_rect[0],
    left_rect[1],
    left_rect[2],
    right_rect[2],
    right_rect[1],
    right_rect[0],
    left_rect[3],
]
print("trial pts", pts)


def area(pts):
    a = 0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2.0


print("area trial", area(pts))


# Compute area of rectangles sum
def rect_area(rect):
    # rect corners in order; compute polygon area
    return area(rect)


print("left area", rect_area(left_rect))
print(
    "left edge lengths",
    [
        math.hypot(
            left_rect[i][0] - left_rect[(i + 1) % 4][0], left_rect[i][1] - left_rect[(i + 1) % 4][1]
        )
        for i in range(4)
    ],
)
# try different orders for right_rect
chosen = [
    (4.576000847997456, -0.26499947000159),
    (5.423999152002544, 0.26499947000159),
    (0.423999152002544, 7.73500052999841),
    (-0.423999152002544, 8.26499947000159),
]
print("explicit chosen area", rect_area(chosen))
orders = [
    right_rect,
    [right_rect[3], right_rect[2], right_rect[1], right_rect[0]],
    [right_rect[2], right_rect[3], right_rect[0], right_rect[1]],
    chosen,
]
for i, o in enumerate(orders):
    print(f"right area order {i}", rect_area(o))
    if len(o) >= 4:
        print(
            " edge lengths:",
            [
                math.hypot(o[j][0] - o[(j + 1) % 4][0], o[j][1] - o[(j + 1) % 4][1])
                for j in range(4)
            ],
        )
print("sum with best order", rect_area(left_rect) + max(rect_area(o) for o in orders))
# overlap area by intersection approx? not computed
