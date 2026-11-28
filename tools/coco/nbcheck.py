"""Polygon checks copied from colab/shared.ipynb (same rules the notebook uses)."""
import numpy as np

def polygon_area(pts):
    """Shoelace area of a polygon given as (n, 2) array (same unit as the points, absolute value)."""
    x, y = pts[:, 0], pts[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))



def polygon_self_intersects(pts):
    """True when two non-adjacent edges cross each other (proper crossings only). Polygons with > 400 points are skipped."""
    n = len(pts)
    if n < 4 or n > 400:
        return False
    a, b = pts, np.roll(pts, -1, axis=0)

    def orient(p, q, r):
        return (q[..., 0] - p[..., 0]) * (r[..., 1] - p[..., 1]) - (q[..., 1] - p[..., 1]) * (r[..., 0] - p[..., 0])

    pa, pb, pc, pd = a[:, None, :], b[:, None, :], a[None, :, :], b[None, :, :]
    crossing = (orient(pa, pb, pc) * orient(pa, pb, pd) < 0) & (orient(pc, pd, pa) * orient(pc, pd, pb) < 0)
    idx = np.arange(n)
    gap = np.abs(idx[:, None] - idx[None, :])
    return bool((crossing & ~((gap <= 1) | (gap == n - 1))).any())



def polygon_problem(pts, width, height):
    """Reason (Vietnamese) why a polygon is invalid for training/scoring, or None."""
    if len(np.unique(np.round(pts, 6), axis=0)) < 3:
        return "ít hơn 3 điểm khác nhau"
    if polygon_self_intersects(pts):
        return "các cạnh tự cắt nhau (đa giác bị xoắn)"
    if polygon_area(pts) * width * height < 1.0:
        return "diện tích gần bằng 0 (nhỏ hơn 1 pixel)"
    return None
