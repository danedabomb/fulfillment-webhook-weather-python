# StockBot Action Code!

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response
from datetime import datetime, timedelta

from google import google
num_page = 3

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    if req.get("result").get("action")=="yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
           return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)
    elif req.get("result").get("action")=="welcome":
        speechText = "Hello there, I'm StockBot!"
        displayText = speechText
        return {
        "speech": speechText,
        "displayText": displayText,
        "source": "apiai-weather-webhook-sample"
    }
    elif req.get("result").get("action")=="getQuote":
        result = req.get("result")
        parameters = result.get("parameters")
        symbol = parameters.get("symbol")
        baseurl = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="
        yql_url = baseurl + symbol + "&interval=1min&apikey=YBUTHZK2W8IUHVPI"
        result = urlopen(yql_url).read()
        now = datetime.now()
        if now.hour > 13:
            time = datetime.now()
            time2 = time.replace(hour=16, minute=00, second=00)
            time3 = str(time2)
            time4 = time3[:-7]
        elif now.hour < 8:
            time = datetime.today() - timedelta(days=1)
            time2 = time.replace(hour=16, minute=00, second=00)
            time3 = str(time2)
            time4 = time3[:-7]
        else:
            time = datetime.now()
            timex = datetime.today() + timedelta(hours=2)
            time2 = timex.replace(second=00)
            time3 = str(time2)
            time4 = time3[:-7]
        data = json.loads(result)
        data1= data['Time Series (1min)'][time4]['1. open']
        speech = symbol + " is currently trading at $" + data1 + "."
        chart_speech = "Chart for " + symbol
        chart_url = "https://www.etoro.com/markets/" + symbol + "/chart"
        speech = speech + " Click the following link for a daily chart: " + chart_url
        return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-weather-webhook-sample"
    }
    elif req.get("result").get("action")=="trackVolume":
        result = req.get("result")
        parameters = result.get("parameters")
        symbol = parameters.get("symbol")
        baseurl = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol="
        yql_url = baseurl + symbol + "&interval=1min&apikey=YBUTHZK2W8IUHVPI"
        result = urlopen(yql_url).read()
        now = datetime.now()
        if now.hour > 13:
            time = datetime.now()
            time2 = time.replace(hour=16, minute=00, second=00)
            time3 = str(time2)
            time4 = time3[:-7]
        elif now.hour < 8:
            time = datetime.today() - timedelta(days=1)
            time2 = time.replace(hour=16, minute=00, second=00)
            time3 = str(time2)
            time4 = time3[:-7]
        else:
            time = datetime.now()
            timex = datetime.today() + timedelta(hours=2)
            time2 = timex.replace(second=00)
            time3 = str(time2)
            time4 = time3[:-7]
        data = json.loads(result)
        data1= data['Time Series (1min)'][time4]['5. volume']
        speech = data1 +  " shares of " + symbol + " have been traded in the last minute."
#        chart_speech = "Chart for " + symbol
#        chart_url = "https://www.etoro.com/markets/" + symbol + "/chart"
#        if source == 'facebook':
#            return {
#                "speech": speech,
#                "displayText": speech,
#                "source": "apiai-wallstreetbot-webhook", 
#                "data": {
#                    “facebook": {
#                      "attachment": {
#                        "type": "template",
#                        "payload": {
#                                "template_type":"button",
#                                "text":speech,
#                                "buttons":[
#                                  {
#                                    "type":"web_url",
#                                    "url":chart_url,
#                                    "title":chart_speech,
#                                    "webview_height_ratio": “compact”,
#                                  },
#                                ]
#                            }
#                         }
#                    }
#                }
#            }
        return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-weather-webhook-sample"
    }
    else:
        return {}
 
    return res

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    speech = "Today the weather in " + location.get('city') + ": " + condition.get('text') + \
             ", And the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
