import unittest
import os
import sys
sys.path.append(os.path.realpath('..'))
from app import *

#--------------------------------------------------------------------------------------------------------------------------------
# COMMENTS:
# 
# 1) Basic testing setup; this is a basic setup does NOT focus on covering all cases,
#    it is only meant to serve as a tool to demonstrate how (unit)testing would work with
#    something like this app.
#--------------------------------------------------------------------------------------------------------------------------------

class TestAppMethods(unittest.TestCase):
    def test_get_SnapTravel_rates(self, city = 'city_string_input', checkin = 'checkin_string_input', checkout = 'checkout_string_input'):
        return self.assertNotEqual(
            first = get_SnapTravel_rates(
                city = city,
                checkin = checkin,
                checkout = checkout
            ),
            second = None,
            msg = "API call should return some data!"
        )
    # def test_get_data(self):
    # def test_get_common_data():
    # def test_get_and_cache_data():
    # def test_cache_data():
    # def test_requests_on_submit_concurrent():
    # def test_get_Hotelscom_rates():

if __name__ == '__main__':
    unittest.main()
