from flask import Flask, render_template, flash, request, redirect, url_for
from forms import HotelListingsForm
import requests
import concurrent.futures
import redis
import json

#--------------------------------------------------------------------------------------------------------------------------------
# COMMENTS:
# 
# 1) This app exhibits the use of the following: Caching(redis), JSON-API calls(Flask), 
#    Concurrent Network requests(concurrent futures), Base app logic(Python), Unit Testing(unittest)
# 2) Can use Celery with RabbitMQ or REDIS for production level code. However, due to time restricition + no necessity to scale,
#    using simple threading to make the concurrent requests here.
# 3) Disregarding data obtained from the form inputs, we are making requests with dummy variables that the public demo API supports.
# 4) Using Redis as the cache for several reasons over some other choices -> based on prior comort due to quick POC nature, would
#    do much more reasearch considering project specific factors in a production environment before commiting to a tool.
#--------------------------------------------------------------------------------------------------------------------------------


# Set up Flask & Redis:
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'
REDIS_BROKER_URL = 'redis://localhost:6379/0'
conn = redis.Redis('localhost')
REDIS_KEYS = ["snaptravel_data", "hotelscom_data"]

@app.route('/', methods=['GET', 'POST'])
def render_form():
    form = HotelListingsForm(request.form, csrf_enabled=False)

    if request.method == 'POST':
        city = request.form['city']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        if form.is_submitted():
          return redirect(url_for('get_data'))

    return render_template('GetHotelListings.html', form=form)

@app.route('/get_data', methods=['GET', 'POST'])
def get_data():
  snaptravel_data, hotelscom_data = get_and_cache_data()
  common_dict = get_common_data(snaptravel_data, hotelscom_data)
  return render_template('HotelsTable.html', data=common_dict)

def get_common_data(snaptravel_data, hotelscom_data):
  snaptravel_hotel_ids = set()
  snaptravel_hotels_data = snaptravel_data["hotels"]
  for snaptravel_hotel_details in snaptravel_hotels_data:
    snaptravel_hotel_ids.add(snaptravel_hotel_details["id"])
  hotelscom_hotel_ids = set()
  hotelscom_hotels_data = hotelscom_data["hotels"]
  for hotelscom_hotel_details in hotelscom_hotels_data:
    hotelscom_hotel_ids.add(hotelscom_hotel_details["id"])
  common_hotel_ids = snaptravel_hotel_ids.intersection(hotelscom_hotel_ids)
  common_hotels_data = {}
  for snaptravel_hotel_details in snaptravel_hotels_data:
    if snaptravel_hotel_details["id"] in common_hotel_ids:
      idval = snaptravel_hotel_details.pop("id")
      price = snaptravel_hotel_details.pop("price")
      snaptravel_hotel_details["snaptravel_price"] = price
      common_hotels_data[idval] = snaptravel_hotel_details
  for hotelscom_hotel_details in hotelscom_data["hotels"]:
    if hotelscom_hotel_details["id"] in common_hotel_ids:
      idval = hotelscom_hotel_details["id"]
      price = hotelscom_hotel_details["price"]
      common_hotels_data[idval]["hotelscom_price"] = price
  return common_hotels_data

def get_and_cache_data(city = 'city_string_input', checkin = 'checkin_string_input', checkout = 'checkout_string_input'):
  snaptravel_data, hotelscom_data = {}, {}
  # Only make requests if data not in cache:
  if conn.exists(REDIS_KEYS[0]) and conn.exists(REDIS_KEYS[1]):
    snaptravel_data = json.loads(conn.get(REDIS_KEYS[0]))
    hotelscom_data = json.loads(conn.get(REDIS_KEYS[1]))
  elif conn.exists(REDIS_KEYS[0]):
    snaptravel_data = json.loads(conn.get(REDIS_KEYS[0]))
    hotelscom_data = get_Hotelscom_rates(city, checkin, checkout)
  elif conn.exists(REDIS_KEYS[1]):
    snaptravel_data = get_SnapTravel_rates(city, checkin, checkout)
    hotelscom_data = json.loads(conn.get(REDIS_KEYS[1]))
  else:
    snaptravel_data, hotelscom_data = requests_on_submit_concurrent(city, checkin, checkout)
  return snaptravel_data, hotelscom_data

def cache_data(snaptravel_data, hotelscom_data):
  conn.set(REDIS_KEYS[0], json.dumps(snaptravel_data))
  conn.set(REDIS_KEYS[1], json.dumps(hotelscom_data))
  return

def requests_on_submit_concurrent(city, checkin, checkout):
  snaptravel_data, hotelscom_data = {}, {}
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    snaptravel_future = executor.submit(get_SnapTravel_rates, city, checkin, checkout)
    hotelscom_future = executor.submit(get_Hotelscom_rates, city, checkin, checkout)
    snaptravel_data = snaptravel_future.result()
    hotelscom_data = hotelscom_future.result()
  cache_data(snaptravel_data, hotelscom_data)
  return snaptravel_data, hotelscom_data

def get_SnapTravel_rates(city, checkin, checkout):
  req_parameters = {
    "city":city, 
    "checkin":checkin, 
    "checkout":checkout, 
    "provider":"snaptravel"
    }
  res = requests.post('https://experimentation.snaptravel.com/interview/hotels', json = req_parameters)
  dictFromServer = res.json()
  return dictFromServer

def get_Hotelscom_rates(city, checkin, checkout):
  req_parameters = {
    "city":city,
    "checkin":checkin, 
    "checkout":checkout, 
    "provider":"retail"
    }
  res = requests.post('https://experimentation.snaptravel.com/interview/hotels', json = req_parameters)
  dictFromServer = res.json()
  return dictFromServer


if __name__ == "__main__":
  app.run(debug=True)