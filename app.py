from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi




ALLOWED_ORIGIN = 'http://127.0.0.1:5501'

app = Flask(__name__)
CORS(app,origins=ALLOWED_ORIGIN)




# MongoDB connection
uri = "mongodb+srv://ozgurokanozdal:okanokan1@bincluester.0iydmxy.mongodb.net/"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["waste_management"]


@app.route('/api/resource/<areaCode>', methods = ["GET"])
def get_resource(areaCode):
    try:
        col = db["bins"]
        data = col.find({"bin_area_code" : int(areaCode)})
        data_list = []

        for item in data:
            data_dict = {
                "id" : str(item["_id"]),
                "bin_lng" : item["bin_lng"],
                "bin_lat" : item["bin_lat"],
                "bin_location_str" : item["bin_location_str"],
                "bin_area_code" : item["bin_area_code"],
                "bin_type_id" : item["bin_type_id"],
                "is_full" : item["is_full"]
            }
            data_list.append(data_dict)

        data.close()
        return jsonify(data_list)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route('/api/resource/<areacode>/optimum-route', methods = ["GET"])
def getRouteByAreaCode(areaCode):
    try:
        col = db["bins"]
        data = col.find({"bin_area_code" : int(areaCode)})
        data_list = []

        for item in data:
            data_dict = {
                "id" : str(item["_id"]),
                "bin_lng" : item["bin_lng"],
                "bin_lat" : item["bin_lat"],
                "bin_location_str" : item["bin_location_str"],
                "bin_area_code" : item["bin_area_code"],
                "bin_type_id" : item["bin_type_id"],
                "is_full" : item["is_full"]
            }
            data_list.append(data_dict)

        data.close()
        return jsonify(data_list)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


def exportData():
    return client

if __name__ == '__main__':
    app.run(debug=True)