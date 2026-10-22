#!/usr/bin/env python3
"""Tests for scripts/boolean_path.py (TD-008 boolean path CLI).

Loaded via importlib from the source script (same pattern as test_export_pptx.py).
Run directly:  python tests/test_boolean_path.py
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import shapely
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "boolean_path.py"
SPEC = importlib.util.spec_from_file_location("boolean_path", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

ELLIPSE_STEPS = MODULE.ELLIPSE_STEPS
OP = {
    "union": MODULE.OP_UNION,
    "combine": MODULE.OP_COMBINE,
    "intersect": MODULE.OP_INTERSECT,
    "subtract": MODULE.OP_SUBTRACT,
    "fragment": MODULE.OP_FRAGMENT,
}


def parse_path(path_str: str) -> Polygon:
    """Re-read a serialized SVG path into a shapely polygon for verification.

    PPTD custom-path semantics: one ``path`` string is ONE shape; the first
    ``M...Z`` ring is the exterior and any further rings are holes of it.
    """
    rings = [
        Polygon(
            [
                tuple(float(n) for n in m)
                for m in re.findall(r"[ML]([\d.+-]+),([\d.+-]+)", seg)
            ]
        )
        for seg in re.findall(r"M[^Z]*Z", path_str)
    ]
    rings = [r for r in rings if len(r.exterior.coords) >= 4]
    if not rings:
        return Polygon()
    if len(rings) == 1:
        return rings[0]
    return Polygon(
        list(rings[0].exterior.coords),
        [list(r.exterior.coords) for r in rings[1:]],
    )


def signed_area(poly: Polygon) -> float:
    """Shoelace signed area of the exterior ring (math y-up convention)."""
    pts = list(poly.exterior.coords)[:-1]  # drop the closing duplicate
    return 0.5 * sum(
        pts[i][0] * pts[(i + 1) % len(pts)][1]
        - pts[(i + 1) % len(pts)][0] * pts[i][1]
        for i in range(len(pts))
    )


class GeometryParsingTests(unittest.TestCase):
    """Slice 1: input JSON schema -> shapely polygons."""

    def test_rect_frame_becomes_box(self):
        polys = MODULE.parse_geometries([{"type": "rect", "frame": [0, 0, 100, 50]}])
        self.assertEqual(len(polys), 1)
        self.assertEqual(polys[0].bounds, (0.0, 0.0, 100.0, 50.0))
        self.assertAlmostEqual(polys[0].area, 5000.0)

    def test_rect_negative_coordinates_kept(self):
        polys = MODULE.parse_geometries([{"type": "rect", "frame": [-50, -20, 100, 50]}])
        self.assertEqual(polys[0].bounds, (-50.0, -20.0, 50.0, 30.0))

    def test_rect_zero_width_or_height_rejected(self):
        for frame in ([0, 0, 0, 50], [0, 0, 50, 0], [0, 0, -5, 50]):
            with self.assertRaises(MODULE.BooleanPathError):
                MODULE.parse_geometries([{"type": "rect", "frame": frame}])

    def test_ellipse_frame_becomes_polygon_approx(self):
        polys = MODULE.parse_geometries([{"type": "ellipse", "frame": [0, 0, 200, 100]}])
        self.assertEqual(len(polys), 1)
        xmin, ymin, xmax, ymax = polys[0].bounds
        self.assertAlmostEqual(xmin, 0.0, places=1)
        self.assertAlmostEqual(ymin, 0.0, places=1)
        self.assertAlmostEqual(xmax, 200.0, places=1)
        self.assertAlmostEqual(ymax, 100.0, places=1)
        # area ~= pi*rx*ry = pi*100*50, within polygonal-approx tolerance
        self.assertAlmostEqual(polys[0].area, math.pi * 100 * 50, delta=math.pi * 100 * 50 * 0.01)
        self.assertEqual(len(polys[0].exterior.coords) - 1, ELLIPSE_STEPS)

    def test_ellipse_zero_dimension_rejected(self):
        for frame in ([0, 0, 0, 100], [0, 0, 100, 0], [0, 0, -1, 100]):
            with self.assertRaises(MODULE.BooleanPathError):
                MODULE.parse_geometries([{"type": "ellipse", "frame": frame}])

    def test_polygon_points_becomes_polygon(self):
        polys = MODULE.parse_geometries(
            [{"type": "polygon", "points": [[0, 0], [100, 0], [100, 100], [0, 100]]}]
        )
        self.assertEqual(polys[0].bounds, (0.0, 0.0, 100.0, 100.0))
        self.assertAlmostEqual(polys[0].area, 10000.0)

    def test_polygon_too_few_points_rejected(self):
        for points in ([[0, 0], [10, 0]], [[0, 0]]):
            with self.assertRaises(MODULE.BooleanPathError):
                MODULE.parse_geometries([{"type": "polygon", "points": points}])

    def test_polygon_self_intersecting_is_made_valid(self):
        # bowtie: self-intersecting, make_valid splits into two triangles
        polys = MODULE.parse_geometries(
            [{"type": "polygon", "points": [[0, 0], [10, 10], [10, 0], [0, 10]]}]
        )
        self.assertGreaterEqual(len(polys), 2)
        # two right triangles, each base 10 x height 5 -> 25 + 25 = 50
        total = sum(p.area for p in polys)
        self.assertAlmostEqual(total, 50.0, delta=1e-6)

    def test_unknown_type_rejected(self):
        with self.assertRaises(MODULE.BooleanPathError):
            MODULE.parse_geometries([{"type": "triangle", "frame": [0, 0, 1, 1]}])

    def test_non_list_input_rejected(self):
        for bad in ({"type": "rect"}, "rect", 42, None):
            with self.assertRaises(MODULE.BooleanPathError):
                MODULE.parse_geometries(bad)

    def test_non_dict_item_rejected(self):
        with self.assertRaises(MODULE.BooleanPathError):
            MODULE.parse_geometries([42, {"type": "rect", "frame": [0, 0, 1, 1]}])

    def test_malformed_frame_rejected(self):
        for frame in ([0, 0, 100], [0, 0, 100, 50, 1], "0,0,100,50", None, [0, 0, "x", 50]):
            with self.assertRaises(MODULE.BooleanPathError):
                MODULE.parse_geometries([{"type": "rect", "frame": frame}])

    def test_malformed_polygon_points_rejected(self):
        for points in ("[[0,0],[1,1]]", [[0, "x"], [1, 1], [2, 2]], None, [[0, 0], [1, 1], [2]]):
            with self.assertRaises(MODULE.BooleanPathError):
                MODULE.parse_geometries([{"type": "polygon", "points": points}])

    def test_collinear_polygon_rejected(self):
        # falsify: degenerate polygon that collapses to no area after validation
        with self.assertRaises(MODULE.BooleanPathError):
            MODULE.parse_geometries(
                [{"type": "polygon", "points": [[0, 0], [1, 1], [2, 2]]}]
            )

    def test_require_shapely_raises_when_missing(self):
        with patch.object(MODULE, "HAS_SHAPELY", False):
            with self.assertRaises(MODULE.ShapelyMissingError) as ctx:
                MODULE.require_shapely()
            self.assertIn("pip install shapely", str(ctx.exception))
            with self.assertRaises(MODULE.ShapelyMissingError):
                MODULE.compute_paths([{"type": "rect", "frame": [0, 0, 1, 1]}], "union")

    def test_empty_input_rejected(self):
        with self.assertRaises(MODULE.BooleanPathError):
            MODULE.parse_geometries([])


TWO_OVERLAP = [
    {"type": "rect", "frame": [0, 0, 100, 100]},
    {"type": "rect", "frame": [50, 50, 100, 100]},
]
TWO_OVERLAP_UNION_AREA = 17500.0  # 100*100 + 100*100 - 50*50
TWO_OVERLAP_INTERSECT_AREA = 2500.0  # 50*50


class ComputePathTests(unittest.TestCase):
    """Slice 2: five boolean operations + output schema + SVG serialization."""

    def test_output_schema_fields_only(self):
        result = MODULE.compute_paths(TWO_OVERLAP, "union")
        self.assertEqual(sorted(result.keys()), ["paths", "viewBox"])
        self.assertIsInstance(result["paths"], list)
        self.assertTrue(all(isinstance(p, str) and p for p in result["paths"]))
        w, h = result["viewBox"]
        self.assertIsInstance(w, (int, float))
        self.assertIsInstance(h, (int, float))
        self.assertGreaterEqual(w, 0)
        self.assertGreaterEqual(h, 0)

    def test_union_area_and_single_path(self):
        result = MODULE.compute_paths(TWO_OVERLAP, "union")
        self.assertEqual(len(result["paths"]), 1)
        poly = parse_path(result["paths"][0])
        self.assertAlmostEqual(poly.area, TWO_OVERLAP_UNION_AREA, delta=0.6)
        self.assertEqual(result["viewBox"], [150.0, 150.0])

    def test_intersect_area_and_translated_viewbox(self):
        result = MODULE.compute_paths(TWO_OVERLAP, "intersect")
        self.assertEqual(len(result["paths"]), 1)
        poly = parse_path(result["paths"][0])
        self.assertAlmostEqual(poly.area, TWO_OVERLAP_INTERSECT_AREA, delta=0.05)
        # result bounds (50,50)-(100,100) -> translated to origin, viewBox 50x50
        self.assertEqual(result["viewBox"], [50.0, 50.0])
        self.assertEqual(poly.bounds, (0.0, 0.0, 50.0, 50.0))

    def test_combine_is_symmetric_difference(self):
        result = MODULE.compute_paths(TWO_OVERLAP, "combine")
        # two disjoint pieces: A\B and B\A
        self.assertEqual(len(result["paths"]), 2)
        total = sum(parse_path(p).area for p in result["paths"])
        expected = TWO_OVERLAP_UNION_AREA - TWO_OVERLAP_INTERSECT_AREA
        self.assertAlmostEqual(total, expected, delta=0.6)

    def test_subtract_first_minus_rest(self):
        result = MODULE.compute_paths(TWO_OVERLAP, "subtract")
        poly = parse_path(result["paths"][0])
        self.assertAlmostEqual(poly.area, 10000.0 - 2500.0, delta=0.6)
        self.assertEqual(len(result["paths"]), 1)

    def test_fragment_overlapping_rects_return_at_least_two_paths(self):
        result = MODULE.compute_paths(TWO_OVERLAP, "fragment")
        self.assertGreaterEqual(len(result["paths"]), 2)
        total = sum(parse_path(p).area for p in result["paths"])
        self.assertAlmostEqual(total, TWO_OVERLAP_UNION_AREA, delta=0.6)

    def test_fragment_single_rect_returns_one_path(self):
        result = MODULE.compute_paths([TWO_OVERLAP[0]], "fragment")
        self.assertEqual(len(result["paths"]), 1)
        self.assertAlmostEqual(parse_path(result["paths"][0]).area, 10000.0, delta=0.05)

    def test_unknown_op_rejected(self):
        with self.assertRaises(MODULE.BooleanPathError):
            MODULE.compute_paths(TWO_OVERLAP, "magic")

    def test_subtract_identical_rects_yields_empty_output(self):
        # falsify: operation that removes everything -> empty paths + warning
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            result = MODULE.compute_paths(
                [{"type": "rect", "frame": [0, 0, 100, 100]}] * 2, "subtract"
            )
        self.assertEqual(result, {"paths": [], "viewBox": [0.0, 0.0]})
        self.assertIn("no area remains", err.getvalue())

    def test_fragment_disjoint_rects_returns_two_paths(self):
        result = MODULE.compute_paths(
            [
                {"type": "rect", "frame": [0, 0, 50, 50]},
                {"type": "rect", "frame": [100, 100, 50, 50]},
            ],
            "fragment",
        )
        self.assertEqual(len(result["paths"]), 2)
        total = sum(parse_path(p).area for p in result["paths"])
        self.assertAlmostEqual(total, 5000.0, delta=0.05)

    def test_union_disjoint_rects_returns_two_paths(self):
        result = MODULE.compute_paths(
            [
                {"type": "rect", "frame": [0, 0, 50, 50]},
                {"type": "rect", "frame": [100, 100, 50, 50]},
            ],
            "union",
        )
        self.assertEqual(len(result["paths"]), 2)
        total = sum(parse_path(p).area for p in result["paths"])
        self.assertAlmostEqual(total, 5000.0, delta=0.05)

    def test_subtract_needs_at_least_two_geometries(self):
        with self.assertRaises(MODULE.BooleanPathError):
            MODULE.compute_paths([TWO_OVERLAP[0]], "subtract")

    def test_single_geometry_identity_for_binary_ops(self):
        for op in ("union", "combine", "intersect"):
            result = MODULE.compute_paths([TWO_OVERLAP[0]], op)
            self.assertEqual(len(result["paths"]), 1)
            self.assertAlmostEqual(parse_path(result["paths"][0]).area, 10000.0, delta=0.05)

    def test_viewbox_derived_from_output_bounds(self):
        result = MODULE.compute_paths(
            [{"type": "rect", "frame": [30, 40, 120, 80]}], "union"
        )
        self.assertEqual(result["viewBox"], [120.0, 80.0])
        poly = parse_path(result["paths"][0])
        self.assertEqual(poly.bounds, (0.0, 0.0, 120.0, 80.0))


class WindingAndSvgTests(unittest.TestCase):
    """Slice 2 (cont.): winding direction + legal SVG path + precision."""

    HOLLOW_RECT = [
        {"type": "rect", "frame": [0, 0, 100, 100]},
        {"type": "rect", "frame": [30, 30, 40, 40]},
    ]

    def test_hollow_outer_cw_inner_ccw(self):
        result = MODULE.compute_paths(self.HOLLOW_RECT, "subtract")
        self.assertEqual(len(result["paths"]), 1)
        poly = parse_path(result["paths"][0])
        self.assertEqual(poly.geom_type, "Polygon")
        self.assertEqual(len(poly.interiors), 1)
        self.assertLess(signed_area(poly), 0)  # exterior CW (math y-up)
        inner = Polygon(list(poly.interiors[0].coords))
        self.assertGreater(signed_area(inner), 0)  # hole CCW

    def test_donut_via_ellipses_has_hole(self):
        result = MODULE.compute_paths(
            [
                {"type": "ellipse", "frame": [0, 0, 200, 200]},
                {"type": "ellipse", "frame": [50, 50, 100, 100]},
            ],
            "subtract",
        )
        poly = parse_path(result["paths"][0])
        self.assertEqual(poly.geom_type, "Polygon")
        self.assertEqual(len(poly.interiors), 1)
        self.assertLess(signed_area(poly), 0)

    def test_legal_svg_path_m_l_z_closed(self):
        result = MODULE.compute_paths(TWO_OVERLAP, "union")
        for path in result["paths"]:
            for seg in re.findall(r"M[^Z]*Z", path):
                self.assertRegex(seg, r"^M[\d.,\-]+(?:L[\d.,\-]+)*Z$")
                self.assertTrue(seg.startswith("M"))
                self.assertTrue(seg.endswith("Z"))

    def test_coordinates_rounded_to_one_decimal(self):
        result = MODULE.compute_paths(
            [{"type": "rect", "frame": [0.44, 0.67, 10.33, 7.22]}], "union"
        )
        path = result["paths"][0]
        tokens = re.findall(r"[ML]([\d.]+),([\d.]+)", path)
        self.assertTrue(tokens)
        for x, y in tokens:
            self.assertRegex(x, r"^\d+\.\d$")
            self.assertRegex(y, r"^\d+\.\d$")
        self.assertIn("10.3", path)
        self.assertIn("7.2", path)
        self.assertEqual(result["viewBox"], [10.3, 7.2])


class CliTests(unittest.TestCase):
    """Slice 3: CLI entry point (stdin/file input, exit codes, errors)."""

    def run_main(self, argv, stdin_text=""):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with patch("sys.stdin", io.StringIO(stdin_text)):
                code = MODULE.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_union_from_stdin_prints_json(self):
        code, out, err = self.run_main(
            ["--op", "union"],
            json.dumps(TWO_OVERLAP),
        )
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(sorted(result.keys()), ["paths", "viewBox"])
        self.assertEqual(len(result["paths"]), 1)

    def test_input_from_file(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "geoms.json"
            path.write_text(json.dumps(TWO_OVERLAP), encoding="utf-8")
            code, out, err = self.run_main(["--op", "union", "--input", str(path)])
            self.assertEqual(code, 0, err)
            result = json.loads(out)
            self.assertEqual(len(result["paths"]), 1)

    def test_missing_input_file_returns_2(self):
        code, out, err = self.run_main(
            ["--op", "union", "--input", r"D:\no-such-dir\missing.json"]
        )
        self.assertEqual(code, 2)
        self.assertIn("cannot read input", err)

    def test_invalid_json_returns_2(self):
        code, out, err = self.run_main(["--op", "union"], "{not json")
        self.assertEqual(code, 2)
        self.assertIn("invalid JSON", err)
        self.assertNotIn("Traceback", err)

    def test_non_array_json_returns_2(self):
        code, out, err = self.run_main(["--op", "union"], '{"type": "rect"}')
        self.assertEqual(code, 2)
        self.assertIn("array", err)

    def test_unknown_geometry_returns_2(self):
        code, out, err = self.run_main(
            ["--op", "union"], json.dumps([{"type": "star", "frame": [0, 0, 1, 1]}])
        )
        self.assertEqual(code, 2)
        self.assertIn("unknown geometry type", err)

    def test_bad_op_exits_via_argparse(self):
        with self.assertRaises(SystemExit) as ctx:
            MODULE.main(["--op", "magic"])
        self.assertEqual(ctx.exception.code, 2)

    def test_missing_op_exits_via_argparse(self):
        with self.assertRaises(SystemExit) as ctx:
            MODULE.main([])
        self.assertEqual(ctx.exception.code, 2)

    def test_subtract_with_one_geometry_returns_2(self):
        code, out, err = self.run_main(
            ["--op", "subtract"], json.dumps([TWO_OVERLAP[0]])
        )
        self.assertEqual(code, 2)
        self.assertIn("at least two geometries", err)

    def test_empty_geometry_array_returns_2(self):
        code, out, err = self.run_main(["--op", "union"], "[]")
        self.assertEqual(code, 2)
        self.assertIn("empty", err)

    def test_main_returns_3_when_shapely_missing_in_process(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with patch.object(MODULE, "HAS_SHAPELY", False):
                code = MODULE.main(["--op", "union"])
        self.assertEqual(code, 3)
        self.assertIn("pip install shapely", err.getvalue())

    def test_script_runs_directly_end_to_end(self):
        # falsify-proof: the file itself is a runnable CLI (covers __main__ guard)
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--op", "union"],
            input=json.dumps(TWO_OVERLAP),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(len(result["paths"]), 1)

    def test_tiny_rect_degrades_to_empty_output(self):
        # falsify: sub-pixel geometry collapses after 1-decimal rounding
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            result = MODULE.compute_paths(
                [{"type": "rect", "frame": [0.04, 0.04, 0.04, 0.04]}], "union"
            )
        self.assertEqual(result, {"paths": [], "viewBox": [0.0, 0.0]})
        self.assertIn("degenerated", err.getvalue())


class SvgSerializationEdgeTests(unittest.TestCase):
    """Falsify edge cases of the public to_svg_path seam."""

    def test_empty_polygon_serializes_to_empty_string(self):
        self.assertEqual(MODULE.to_svg_path(Polygon()), "")

    def test_tiny_ring_collapses_after_rounding(self):
        poly = Polygon([(0, 0), (0.04, 0), (0.04, 0.04), (0, 0.04)])
        self.assertEqual(MODULE.to_svg_path(poly), "")

    def test_negative_zero_coordinate_formats_as_zero(self):
        # falsify: -0.0 must not leak into the SVG output as "-0.0"
        poly = Polygon([(-0.0, -0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)])
        path = MODULE.to_svg_path(poly)
        self.assertNotIn("-0.0", path)
        self.assertTrue(path.startswith("M0.0,0.0"))


class SoftDependencyTests(unittest.TestCase):
    """Slice 4: shapely missing -> clear error + install hint, no traceback."""

    def _run_without_shapely(self):
        env_code = (
            "import importlib.util, sys\n"
            "from pathlib import Path\n"
            "sys.modules['shapely'] = None\n"
            f"spec = importlib.util.spec_from_file_location('boolean_path', {SCRIPT.as_posix()!r})\n"
            "m = importlib.util.module_from_spec(spec)\n"
            "assert spec and spec.loader\n"
            "spec.loader.exec_module(m)\n"
            "assert m.HAS_SHAPELY is False\n"
            "try:\n"
            "    m.compute_paths([{'type': 'rect', 'frame': [0, 0, 1, 1]}], 'union')\n"
            "    print('API_NO_RAISE')\n"
            "except m.ShapelyMissingError:\n"
            "    print('API_RAISED')\n"
            "raise SystemExit(m.main(['--op', 'union']))\n"
        )
        return subprocess.run(
            [sys.executable, "-c", env_code],
            input="[]",
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_cli_reports_install_hint_and_exits_nonzero(self):
        proc = self._run_without_shapely()
        self.assertEqual(proc.returncode, 3)
        self.assertIn("pip install shapely", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_api_raises_shapely_missing_error(self):
        proc = self._run_without_shapely()
        self.assertIn("API_RAISED", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
