#!/usr/bin/env python3
"""TD-008: Boolean path CLI — compute combined / hollow-out shapes for PPTD.

Reads a JSON array of geometry objects (rect / ellipse / polygon, coordinates
aligned to PPTD bounds, origin at top-left) and emits SVG path strings that can
be written straight into a PPTD element with ``shapeName: "custom"``::

    {"paths": ["M0,0L100,0...Z", "..."], "viewBox": [w, h]}

Five boolean operations are provided via ``--op``::

    union      -> shapely unary_union            (glue shapes together)
    combine    -> shapely symmetric_difference   (XOR: union minus intersection)
    intersect  -> shapely intersection           (common area only)
    subtract   -> shapely difference             (first geometry minus the rest)
    fragment   -> shapely ops.polygonize         (split overlapping inputs)

Winding follows the PPTD hollow-out convention: every output polygon is
re-oriented with ``shapely.geometry.polygon.orient(p, -1)`` so the outer ring
is clockwise and inner rings (holes) are counter-clockwise. Coordinates are
rounded to 1 decimal place; the ``viewBox`` derives from the output bounds.

``shapely`` is a soft dependency: when it is missing the CLI reports a clear
error with an install hint instead of crashing with a traceback.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

try:
    from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, box
    from shapely.geometry.polygon import orient
    from shapely.ops import polygonize, unary_union
    from shapely.validation import make_valid

    HAS_SHAPELY = True
except ImportError as _exc:  # pragma: no cover - exercised via subprocess
    HAS_SHAPELY = False
    _SHAPELY_IMPORT_ERROR = _exc

__all__ = [
    "BooleanPathError",
    "ShapelyMissingError",
    "OP_UNION",
    "OP_COMBINE",
    "OP_INTERSECT",
    "OP_SUBTRACT",
    "OP_FRAGMENT",
    "OPERATIONS",
    "ELLIPSE_STEPS",
    "MAX_COORD",
    "parse_geometries",
    "compute_paths",
    "to_svg_path",
    "main",
]

# --- operation names --------------------------------------------------------
OP_UNION = "union"
OP_COMBINE = "combine"
OP_INTERSECT = "intersect"
OP_SUBTRACT = "subtract"
OP_FRAGMENT = "fragment"
OPERATIONS: Tuple[str, ...] = (
    OP_UNION,
    OP_COMBINE,
    OP_INTERSECT,
    OP_SUBTRACT,
    OP_FRAGMENT,
)

# Number of sample points used to approximate an ellipse as a polygon.
ELLIPSE_STEPS = 64

# Sane coordinate bound in PPTD px. Coordinates beyond this are rejected up
# front: their 1-decimal formatting would otherwise overflow into illegal
# "inf" / "1e+308" output (review F1/F2).
MAX_COORD = 1_000_000.0


class BooleanPathError(ValueError):
    """Raised for invalid CLI/JSON input or degenerate geometry."""


class ShapelyMissingError(RuntimeError):
    """Raised when shapely is not installed and a computation is attempted."""


SHAPELY_INSTALL_HINT = (
    "shapely is required to compute boolean paths but is not installed. "
    "Install it with: pip install shapely"
)


def require_shapely() -> None:
    """Raise :class:`ShapelyMissingError` when the soft dependency is absent."""
    if not HAS_SHAPELY:
        raise ShapelyMissingError(SHAPELY_INSTALL_HINT)


def _num(value: Any, what: str) -> float:
    """Coerce a JSON number, rejecting booleans / strings / None and any
    non-finite or out-of-range value (review F1/F2)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BooleanPathError(f"{what} must be a number, got {value!r}")
    result = float(value)
    if not math.isfinite(result) or abs(result) > MAX_COORD:
        raise BooleanPathError(
            f"{what} must be a finite number within ±{MAX_COORD:g}, got {value!r}"
        )
    return result


def _frame_of(spec: Dict[str, Any], kind: str) -> Tuple[float, float, float, float]:
    """Read and validate a ``frame: [x, y, w, h]`` field."""
    frame = spec.get("frame")
    if not isinstance(frame, (list, tuple)) or len(frame) != 4:
        raise BooleanPathError(
            f"{kind} requires frame [x, y, w, h], got {frame!r}"
        )
    return tuple(_num(v, "frame coordinate") for v in frame)  # type: ignore[return-value]


def _ellipse_polygon(x: float, y: float, w: float, h: float) -> Polygon:
    """Approximate an axis-aligned ellipse as a closed sample-point polygon."""
    rx, ry = w / 2.0, h / 2.0
    cx, cy = x + rx, y + ry
    points = [
        (
            cx + rx * math.cos(2.0 * math.pi * i / ELLIPSE_STEPS),
            cy + ry * math.sin(2.0 * math.pi * i / ELLIPSE_STEPS),
        )
        for i in range(ELLIPSE_STEPS)
    ]
    return Polygon(points)


def _points_of(spec: Dict[str, Any]) -> List[Tuple[float, float]]:
    """Read and validate a ``points: [[x, y], ...]`` polygon field."""
    points = spec.get("points")
    if not isinstance(points, (list, tuple)):
        raise BooleanPathError(f"polygon requires points [[x, y], ...], got {points!r}")
    if len(points) < 3:
        raise BooleanPathError(
            f"polygon needs at least 3 points, got {len(points)}"
        )
    out: List[Tuple[float, float]] = []
    for pt in points:
        if not isinstance(pt, (list, tuple)) or len(pt) != 2:
            raise BooleanPathError(f"polygon point must be [x, y], got {pt!r}")
        out.append((_num(pt[0], "point x"), _num(pt[1], "point y")))
    return out


def _polygons_from(geom: Any) -> List[Polygon]:
    """Flatten a shapely geometry into its area polygons (ignore lines/points)."""
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    if geom.geom_type == "MultiPolygon":
        return list(geom.geoms)
    if geom.geom_type == "GeometryCollection":
        out: List[Polygon] = []
        for part in geom.geoms:
            out.extend(_polygons_from(part))
        return out
    return []


def geometry_to_shapely(spec: Dict[str, Any]) -> List[Polygon]:
    """Convert one JSON geometry object into one or more shapely polygons.

    ``rect`` and ``ellipse`` map to a single polygon; a ``polygon`` input that
    self-intersects is repaired with :func:`shapely.validation.make_valid`,
    which may split it into several valid polygons.
    """
    kind = spec.get("type")
    if kind == "rect":
        x, y, w, h = _frame_of(spec, "rect")
        if w <= 0 or h <= 0:
            raise BooleanPathError(
                f"rect frame must have positive width and height, got {w}x{h}"
            )
        return [box(x, y, x + w, y + h)]
    if kind == "ellipse":
        x, y, w, h = _frame_of(spec, "ellipse")
        if w <= 0 or h <= 0:
            raise BooleanPathError(
                f"ellipse frame must have positive width and height, got {w}x{h}"
            )
        return [_ellipse_polygon(x, y, w, h)]
    if kind == "polygon":
        points = _points_of(spec)
        valid = make_valid(Polygon(points))
        polys = _polygons_from(valid)
        if not polys:
            raise BooleanPathError("polygon collapses to no area after validation")
        return polys
    raise BooleanPathError(
        f"unknown geometry type {kind!r}; expected one of rect / ellipse / polygon"
    )


def parse_geometries(data: Any) -> List[Polygon]:
    """Validate the input JSON geometry array and convert it to shapely polygons.

    Args:
        data: the parsed JSON value, expected to be a non-empty list of
            geometry objects ``[{"type": "rect"|"ellipse"|"polygon", ...}]``.

    Returns:
        The list of shapely polygons, one per rect/ellipse and potentially
        several for repaired self-intersecting polygons.

    Raises:
        BooleanPathError: when the input is not a JSON array, is empty, or
            contains a malformed / unknown geometry object.
        ShapelyMissingError: when the soft dependency ``shapely`` is missing.
    """
    require_shapely()
    if not isinstance(data, list):
        raise BooleanPathError(
            "input must be a JSON array of geometry objects, got "
            f"{type(data).__name__}"
        )
    if not data:
        raise BooleanPathError(
            "input geometry array is empty; provide at least one geometry"
        )
    polygons: List[Polygon] = []
    for spec in data:
        if not isinstance(spec, dict):
            raise BooleanPathError(f"each geometry must be an object, got {spec!r}")
        polygons.extend(geometry_to_shapely(spec))
    return polygons


def _fmt(value: float) -> str:
    """Format a coordinate with exactly one decimal place."""
    if value == 0.0:
        value = 0.0  # normalize -0.0 -> 0.0 so output stays clean
    return f"{value:.1f}"


def _round1(value: float) -> float:
    """Round a coordinate to one decimal place (same rule as :func:`_fmt`)."""
    return float(_fmt(value))


def to_svg_path(poly: Polygon, dx: float = 0.0, dy: float = 0.0) -> str:
    """Serialize an oriented polygon to an SVG path string.

    Each ring becomes ``M...L...Z`` with coordinates shifted by ``(dx, dy)``
    and rounded to one decimal place. Degenerate rings are skipped: a ring is
    degenerate when, after translation and rounding, it has fewer than three
    distinct points **or** a zero shoelace area (e.g. three collinear points,
    or an ``A, B, A`` ring). This is the same criterion every other ring
    serializer uses (see :func:`_normalize_ring`). The caller is responsible
    for winding (see :func:`compute_paths`).

    Args:
        poly: the polygon to serialize (exterior + holes).
        dx: horizontal translation applied to every coordinate.
        dy: vertical translation applied to every coordinate.

    Returns:
        A legal SVG path string whose segments use only ``M``/``L``/``Z``
        commands and end with ``Z``; the empty string when every ring is
        degenerate.
    """
    if poly is None or poly.is_empty:
        return ""
    parts: List[str] = []
    for ring in (poly.exterior, *poly.interiors):
        uniq = _normalize_ring(ring, dx, dy)
        if uniq is None:
            continue
        parts.append("M" + _fmt(uniq[0][0]) + "," + _fmt(uniq[0][1]))
        for x, y in uniq[1:]:
            parts.append("L" + _fmt(x) + "," + _fmt(y))
        parts.append("Z")
    return "".join(parts)


def _shoelace_area(pts: Sequence[Tuple[float, float]]) -> float:
    """Absolute shoelace area of an open ring of points (all edges incl. wrap)."""
    n = len(pts)
    if n < 3:
        return 0.0
    return 0.5 * abs(
        sum(
            pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
            for i in range(n)
        )
    )


def _normalize_ring(
    ring: Any, dx: float, dy: float
) -> Optional[List[Tuple[float, float]]]:
    """Round + translate one ring and judge it against the single
    degenerate-ring contract shared by every ring-serializing caller (TD-016).

    A ring is degenerate — and returns ``None`` — when, after translation and
    rounding to one decimal, it has fewer than three distinct points or a zero
    shoelace area (e.g. three collinear points, an ``A, B, A`` ring whose
    adjacent-duplicate removal still leaves three entries, or a >=3-point
    zig-zag that is collinear after rounding). Such rings must be dropped,
    never serialized as zero-area paths.

    Args:
        ring: a shapely ring (``poly.exterior`` or one of ``poly.interiors``).
        dx: horizontal translation subtracted from every x coordinate.
        dy: vertical translation subtracted from every y coordinate.

    Returns:
        The ring's points as ``(x, y)`` pairs with the closing duplicate and
        consecutive duplicates removed, or ``None`` when it is degenerate.
    """
    pts = [(_round1(c[0] - dx), _round1(c[1] - dy)) for c in ring.coords]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    uniq: List[Tuple[float, float]] = []
    for pt in pts:
        if not uniq or pt != uniq[-1]:
            uniq.append(pt)
    if len(set(uniq)) < 3:
        return None
    if _shoelace_area(uniq) <= 0.0:
        return None
    return uniq


def _rounded_ring(ring: Any, dx: float, dy: float) -> Optional[List[Tuple[float, float]]]:
    """Backwards-compatible alias of :func:`_normalize_ring`.

    Kept as the name used by :func:`compute_paths`; it delegates so the
    degenerate-ring criterion exists in exactly one place (TD-016).
    """
    return _normalize_ring(ring, dx, dy)


# Rings whose area is at or below this (in square units) are considered
# degenerate after the 1-decimal rounding and dropped with a stderr warning.
EPS_AREA = 1e-6


def _orient_polygon(poly: Polygon, seen: Set[str]) -> Polygon:
    """Re-orient a polygon: outer ring CW, inner rings CCW, and drop
    degenerate (zero-area) rings so the rounded output stays sane.

    Args:
        poly: the polygon to re-orient.
        seen: the calling computation's warning de-duplication container.

    Returns:
        The re-oriented polygon, or an empty ``Polygon`` for a zero-area input.
    """
    dropped = False
    if poly.area <= EPS_AREA:
        return Polygon()
    interiors: List[Any] = []
    for ring in poly.interiors:
        if ring is None or len(ring.coords) < 4:
            dropped = True
            continue
        if abs(Polygon(ring).area) <= EPS_AREA:
            dropped = True
            continue
        interiors.append(ring)
    out = orient(Polygon(poly.exterior, interiors), -1.0)
    if dropped:
        _warn("dropped a degenerate ring (zero area after rounding)", seen)
    return out


def _warn(message: str, seen: Set[str]) -> None:
    """Emit a stderr warning, deduplicated within one computation (TD-019).

    Args:
        message: the warning text; also the de-duplication key.
        seen: the caller-owned de-duplication container. Every computation
            passes its own set so nested or concurrent runs never share —
            and never reset — each other's warning state.
    """
    if message not in seen:
        seen.add(message)
        print(f"boolean_path: warning: {message}", file=sys.stderr)


def _apply_operation(polys: List[Polygon], op: str) -> Any:
    """Apply the requested boolean operation over the given polygons."""
    if op == OP_UNION:
        return unary_union(polys)
    if op == OP_COMBINE:
        result = polys[0]
        for other in polys[1:]:
            result = result.symmetric_difference(other)
        return result
    if op == OP_INTERSECT:
        result = polys[0]
        for other in polys[1:]:
            result = result.intersection(other)
        return result
    if op == OP_SUBTRACT:
        cutter = unary_union(polys[1:])
        return polys[0].difference(cutter)
    if op == OP_FRAGMENT:
        lines = [p.boundary for p in polys if not p.is_empty]
        # Node the boundary lines first: polygonize only splits where the
        # input linework is already noded at crossings.
        pieces = [
            piece
            for piece in polygonize(unary_union(lines))
            if piece.geom_type == "Polygon" and not piece.is_empty
        ]
        if not pieces:
            return None
        if len(pieces) == 1:
            return pieces[0]
        return MultiPolygon(pieces)
    raise BooleanPathError(
        f"unknown operation {op!r}; expected one of {', '.join(OPERATIONS)}"
    )


def compute_paths(geometries: Any, op: str) -> Dict[str, Any]:
    """Compute boolean SVG paths from a JSON geometry array.

    Args:
        geometries: the parsed JSON value — a non-empty list of geometry
            objects ``[{"type": "rect"|"ellipse"|"polygon", ...}, ...]`` whose
            coordinates are aligned to PPTD bounds (px, origin top-left).
        op: one of ``union`` / ``combine`` / ``intersect`` / ``subtract`` /
            ``fragment``.

    Returns:
        ``{"paths": [svg-path, ...], "viewBox": [w, h]}`` where every path is a
        legal SVG path string (start ``M``, closed ``Z``, outer ring CW / inner
        rings CCW per the PPTD hollow-out convention, coordinates rounded to 1
        decimal) and ``viewBox`` is the non-negative output bounding-box size.
        The output can be written directly into a PPTD element with
        ``shapeName: "custom"`` (fields ``path`` / ``viewBox``).

    Raises:
        BooleanPathError: malformed input, unknown ``op``, or an operation
            that the geometry count cannot satisfy (e.g. ``subtract`` with
            fewer than two geometries).
        ShapelyMissingError: when the soft dependency ``shapely`` is missing.
    """
    require_shapely()
    if op not in OPERATIONS:
        raise BooleanPathError(
            f"unknown operation {op!r}; expected one of {', '.join(OPERATIONS)}"
        )
    # Warnings are deduplicated within this computation only: the de-dup
    # container is local, so nested / concurrent runs cannot reset it (TD-019).
    seen: Set[str] = set()
    polygons = parse_geometries(geometries)
    if op == OP_SUBTRACT and len(polygons) < 2:
        raise BooleanPathError(
            "subtract needs at least two geometries (first minus the rest)"
        )
    result = _apply_operation(polygons, op)
    out_polys = [p for p in _polygons_from(result) if not p.is_empty]
    out_polys = [
        p for p in (_orient_polygon(p, seen) for p in out_polys) if not p.is_empty
    ]
    if not out_polys:
        _warn("no area remains after the boolean operation; output is empty", seen)
        return {"paths": [], "viewBox": [0.0, 0.0]}

    minx = min(c[0] for p in out_polys for r in (p.exterior, *p.interiors) for c in r.coords)
    miny = min(c[1] for p in out_polys for r in (p.exterior, *p.interiors) for c in r.coords)

    # Round to one decimal and drop rings that degenerate after rounding
    # (fewer than 3 distinct points or zero shoelace area — review F3).
    built: List[Polygon] = []
    for poly in out_polys:
        exterior = _rounded_ring(poly.exterior, minx, miny)
        if exterior is None:
            _warn("dropped a degenerate ring (zero area after rounding)", seen)
            continue
        interiors: List[List[Tuple[float, float]]] = []
        for ring in poly.interiors:
            rounded = _rounded_ring(ring, minx, miny)
            if rounded is None:
                _warn("dropped a degenerate ring (zero area after rounding)", seen)
            else:
                interiors.append(rounded)
        built.append(Polygon(exterior, interiors))

    if not built:
        _warn("all output rings degenerated after rounding; output is empty", seen)
        return {"paths": [], "viewBox": [0.0, 0.0]}

    # viewBox: bounds of the final RETAINED (post-rounding) rings only, so a
    # dropped ring never inflates it (review F4).
    xs = [c[0] for p in built for r in (p.exterior, *p.interiors) for c in r.coords]
    ys = [c[1] for p in built for r in (p.exterior, *p.interiors) for c in r.coords]
    view_box = [_round1(max(xs) - min(xs)), _round1(max(ys) - min(ys))]

    paths = [to_svg_path(p) for p in built]
    paths = [p for p in paths if p]
    if not paths:
        _warn("all output rings degenerated after rounding; output is empty", seen)
        return {"paths": [], "viewBox": [0.0, 0.0]}
    return {"paths": paths, "viewBox": [float(v) for v in view_box]}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="boolean_path",
        description=(
            "Compute boolean SVG paths (union / combine / intersect / subtract / "
            "fragment) from a JSON geometry array and print "
            '{"paths": [...], "viewBox": [w, h]} for PPTD shapeName="custom".'
        ),
        epilog=(
            "Input: a JSON array of geometry objects on stdin (or --input FILE): "
            '[{"type":"rect","frame":[x,y,w,h]}, '
            '{"type":"ellipse","frame":[x,y,w,h]}, '
            '{"type":"polygon","points":[[x,y],...]}]'
        ),
    )
    parser.add_argument(
        "--op",
        required=True,
        choices=OPERATIONS,
        help="boolean operation: " + " / ".join(OPERATIONS),
    )
    parser.add_argument(
        "--input",
        metavar="FILE",
        help="read the geometry JSON from FILE instead of stdin",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the boolean-path CLI and return the process exit code.

    Args:
        argv: command-line arguments (defaults to ``sys.argv[1:]``).

    Returns:
        ``0`` on success, ``2`` for input/JSON/geometry errors and ``3`` when
        the soft dependency ``shapely`` is missing.
    """
    args = build_parser().parse_args(argv)
    if not HAS_SHAPELY:
        print(f"boolean_path: {SHAPELY_INSTALL_HINT}", file=sys.stderr)
        return 3
    try:
        raw = (
            Path(args.input).read_text(encoding="utf-8")
            if args.input
            else sys.stdin.read()
        )
    except OSError as exc:
        print(f"boolean_path: cannot read input: {exc}", file=sys.stderr)
        return 2
    try:
        data = json.loads(raw)
        result = compute_paths(data, args.op)
    except json.JSONDecodeError as exc:
        print(f"boolean_path: invalid JSON: {exc}", file=sys.stderr)
        return 2
    except BooleanPathError as exc:
        print(f"boolean_path: {exc}", file=sys.stderr)
        return 2
    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())