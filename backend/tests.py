import unittest
from app import app, is_within_radius, USC_COORDINATES

class RouteTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_is_within_radius(self):
        within_point = (34.0219, -118.2841)  # Close to USC
        outside_point = (34.0522, -118.2437)  # Downtown LA, far from USC

        self.assertTrue(is_within_radius(within_point, USC_COORDINATES, 2))
        self.assertFalse(is_within_radius(outside_point, USC_COORDINATES, 2))

    def test_create_route_within_radius(self):
        response = self.app.post('/api/route', json={
            'start': 'USC',  # Assuming get_coordinates() returns valid points
            'end': 'USC'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Route is within the 2-mile radius of USC', response.get_json()['message'])

    def test_create_route_outside_radius(self):
        response = self.app.post('/api/route', json={
            'start': 'Downtown LA',
            'end': 'USC'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Start point is not within a 2-mile radius of USC', response.get_json()['error'])

def main():
    unittest.main()

main()