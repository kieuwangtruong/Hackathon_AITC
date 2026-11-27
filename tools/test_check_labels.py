"""Regression cases for topology and numeric errors that used to pass validation."""
import pathlib
import tempfile
import unittest

from check_labels import check_file, polygon_crosses


class LabelValidationTests(unittest.TestCase):
    def check_text(self, text):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'label.txt'
            p.write_text(text, encoding='utf-8')
            return check_file(p)

    def test_bowtie_rejected(self):
        self.assertTrue(self.check_text('0 0 0 1 1 0 1 1 0')[0])

    def test_non_finite_rejected(self):
        for value in ['nan', 'inf', '-inf']:
            with self.subTest(value=value):
                self.assertTrue(self.check_text(f'0 0 0 1 0 1 {value}')[0])

    def test_triangle_accepted(self):
        errors, warnings, classes = self.check_text('9 .1 .1 .3 .5 .7 .2')
        self.assertEqual(errors, [])
        self.assertEqual(classes, [9])

    def test_empty_background_allowed(self):
        self.assertEqual(self.check_text(''), ([], [], []))

    def test_retraced_bridge_warns(self):
        # Two squares connected by an edge traversed in both directions.
        text = '5 0 0 .2 0 .2 .2 .8 .8 1 .8 1 1 .8 1 .8 .8 .2 .2 0 .2'
        errors, warnings, classes = self.check_text(text)
        self.assertEqual(errors, [])
        self.assertTrue(any('bridge' in w for w in warnings))

    def test_crossing_over_400_vertices_detected(self):
        points = [(0., 0.), (1., 1.), (0., 1.), (1., 0.)]
        points += [(1 - k / 500, 0.) for k in range(1, 450)]
        self.assertTrue(polygon_crosses(points))


if __name__ == '__main__':
    unittest.main()
