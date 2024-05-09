from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from route import calculateGraph




ALLOWED_ORIGIN = 'http://127.0.0.1:5501'

app = Flask(__name__)

CORS(app,origins=ALLOWED_ORIGIN)


uri = "mongodb+srv://ozgurokanozdal:okanokan1@bincluester.0iydmxy.mongodb.net/"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["waste_management"]


# areaCode a göre bütün çöp kutularını döner
@app.route('/api/resource/<areaCode>', methods = ["GET"])
def getAllBinsByAreaCode(areaCode):
    try:
        col = db["bins"]
        data = col.find({"bin_area_code" : int(areaCode)})

        data_list = convertBins(data)

        data.close()
        return jsonify(data_list)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


# area code a göre bütün dolu çöp kutularını döner
@app.route('/api/resource/<areaCode>', methods = ["GET"])
def getAllFullBinByAreaCode(areaCode):
    try:
        col = db["bins"]
        data = col.find({"bin_area_code" : int(areaCode), "is_full" : 1})

        data_list = convertBins(data)

        data.close()
        return jsonify(data_list)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


# areaCode a göre optimum rota döner (DJİKSTRA)
@app.route('/api/resource/<areacode>/optimum-route', methods = ["GET"])
def getRouteByAreaCode(areaCode):
    try:
        col = db["bins"]
        bins_full = col.find({"bin_area_code" : int(areaCode), "is_full" : 1}) #şu an bu bölgedeki dolu kutular döndü
        # graph = db["graphs"]

        #  graphı varsa bu bölgenin graphı alınacak
        # currentGraph = graph.find({"graph_area_code" : int(areaCode)}) #burada şu anki bölgenin dbdeki graphı döndü

        #  graphı yoksa graph hesaplanacak ama uzun sürüyor--> timeout yiyebilir?
        # createGraph endpointi ile graphi başka yerde oluşturulsun burada var olanlar incelensin yoksa ise 404 dönsün

        #  djikstra ile optimum rota hesaplanacak 
        # json formatında optimum rota başlangıçtan sona kadar cliente gönderilecek
        # eğer mümkünse en baştan toplam yolculuk süresi gibi veriler de yollanabilirse süper olur
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route("/api/create-graph/<areaCode>", methods = ["POST"])
def createGraphByAreaCode(areaCode):
    col = db["graph"]
    graph = col.find_one({"graph_area_code" : int(areaCode)})
    colbins = db["bins"]

    
    if(graph is None):
        binsRaw = colbins.find({"bin_area_code" : int(areaCode)})
        bins = convertBins(binsRaw)

        if len(bins) > 2:
            graph_created = calculateGraph.calculateGraph(bins)
            result = col.insert_one({"graph_area_code": int(areaCode), "graph" : graph_created})
            if result.inserted_id:
                return jsonify({"message": "Graph created succesfully"}),200
            else:
                return jsonify({"error" : "Failed to create graph"}),500
        else:
            return jsonify({"error": "Bins data not found for the provided areaCode"}), 404
    else:
        return jsonify({"error" : "This graph already exists"}),409


@app.route("/api/update-graph/<areaCode>", methods=["UPDATE"])
def updateGraphByAreaCode(areaCode):
    # bölge koduna ait graph yok ise 404

    # var ise aynı bölgedeki bütün noktaları alıp tekrar graph oluştur. BURASI UZUN SÜRECEK? timeout yiyebilir mi? dene ve yanıl
    return 1


@app.route("/api/discharge/<binId>", methods = ["UPDATE"])
def dischargeBinByBinId(binId):
    # bin id yok ise 404 dönsün

    # db.collectionName.findById('objectIdHere') -- id ile döndürme

    # var ise çöp kutusunu bulsun ve is_full fieldını 1 ise 0 yapsın değilse bir şey yapmasın
    return 1

@app.route("/api/fill/<binId>", methods = ["UPDATE"])
def fillBinByBinId(binId):
    # bin id yoksa 404 dönsün

    
    # db.collectionName.findById('objectIdHere') -- id ile döndürme
    
    # var ve is_full 0 ise 1 yapsın değilse bir şey yapmasın
    return 1



def exportData():
    return client

def convertBins(data):
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
    return data_list


if __name__ == '__main__':
    app.run(debug=True)