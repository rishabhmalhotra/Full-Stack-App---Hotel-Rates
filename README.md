## To Run
Check out RUN_INSTRUCTIONS for steps to run.

## WHAT DOES THIS PROJECT IMPLEMENT?

This project demonstrates the use of the following basic technologies:
  - Caching(redis)
  - JSON based API calls(Flask)
  - Concurrent Network requests(concurrent futures)
  - Base app logic(Python)
  - Unit Testing(unittest)

Here, I implement a flask web app that serves html.
All dependencies are specified in requirements.txt
The service will be running at http://127.0.0.1:5000/.

**Step 1**

The app loads a form with some fields for ingesting input. The form also has a SUBMIT button.
To keep the app simple, we do not worry about form validation or any styling.

**Step 2**

When the form is submitted, **2 HTTP POST requests** are made in parallel to snaptravel,com and Hotels.com APIs with the following request body

```
{
  city : city_string_input,
  checkin : checkin_string_input,
  checkout : checkout_string_input,
  provider : 'snaptravel' OR 'retail'
}
```

The responses will be in json and each response will have an array of hotels and prices.
```
[{
  id : 12,
  hotel_name : 'Center Hilton',
  num_reviews : 209,
  address : '12 Wall Street, Very Large City',
  num_stars : 4,
  amenities : ['Wi-Fi', 'Parking'],
  image_url : 'https://images.trvl-media.com/hotels/1000000/20000/19600/19558/19558_410_b.jpg',
  price : 132.11
},
...
]
```

The app then caches these responses in the server, in whatever way that seems fit using redis.

**Step 3**

After both these calls have returned, we take **only** the hotels that appear in both the responses and return an html table with the data.
