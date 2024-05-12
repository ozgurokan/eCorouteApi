from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from route import calculateGraph
from route import djikstra




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
@app.route('/api/resource/optimum-route/<areaCode>', methods = ["GET"])
def getRouteByAreaCode(areaCode):
    try:
        col = db["bins"]
        colGraph = db["graph"]
        bins_full = col.find({"bin_area_code" : int(areaCode), "is_full" : 1}) #şu an bu bölgedeki dolu kutular döndü
        graph_from_db = colGraph.find_one({"graph_area_code" : int(areaCode)})

        if (graph_from_db is not None):
            graph_for_djikstra = graph_from_db["graph"]
            g = djikstra.Graph(len(graph_for_djikstra))
            g.graph = graph_for_djikstra
           

            return jsonify(graph_from_db["graph"])
        else:
             # createGraph endpointi ile graphi başka yerde oluşturulsun burada var olanlar incelensin yoksa ise 404 dönsün
            return jsonify({"error" : "There is no graph information for this area"}), 404
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


#  graph oluşturma
@app.route("/api/create-graph/<areaCode>", methods = ["POST"])
def createGraphByAreaCode(areaCode):
    col = db["graph"]
    graph = col.find_one({"graph_area_code" : int(areaCode)})
    colbins = db["bins"]

    
    if(graph is None):
        binsRaw = colbins.find({"bin_area_code" : int(areaCode)})
        bins = convertBins(binsRaw)
        ids = dict()

        if len(bins) > 2:
            for i in range(len(bins)):
                ids[str(i)] = {"index" : i, "id" : bins[i]["id"]}
                print(ids)
            graph_created = calculateGraph.calculateGraph(bins)

            result = col.insert_one({"graph_area_code": int(areaCode), "graph" : graph_created , "id_list" : ids})
            if result.inserted_id:
                return jsonify({"message": "Graph created succesfully"}),200
            else:
                return jsonify({"error" : "Failed to create graph"}),500
        else:
            return jsonify({"error": "Bins data not found for the provided areaCode"}), 404
    else:
        return jsonify({"error" : "This graph already exists"}),409



#  graph güncelleme
@app.route("/api/update-graph/<areaCode>", methods=["UPDATE"])
def updateGraphByAreaCode(areaCode):
    col = db["graph"]
    graph = col.find_one({"graph_area_code" : int(areaCode)})


    if(graph is not None):
        colbins = db["bins"]
        binsRaw = colbins.find({"bin_area_code" : int(areaCode)})
        bins = convertBins(binsRaw)
        if len(bins) > 2:
            graph_created = calculateGraph.calculateGraph(bins)
            result = col.update_one({"graph_area_code": int(areaCode), "graph" : graph_created})
            if result.inserted_id:
                return jsonify({"message": "Graph updated succesfully"}),200
            else:
                return jsonify({"error" : "Failed to update graph"}),500
        return bin_ids
    else:
        return jsonify({"error" : "Graph not found"}),404
   

#  kutuyu alındı olarak işaretlendikten sonra dbde is_full'u boşaltacak endpoint 
# rota da her sonraki dendiğinde bu endpointe update atılacak
@app.route("/api/discharge/<binId>", methods = ["UPDATE"])
def dischargeBinByBinId(binId):
    # bin id yok ise 404 dönsün

    # db.collectionName.findById('objectIdHere') -- id ile döndürme

    # var ise çöp kutusunu bulsun ve is_full fieldını 1 ise 0 yapsın değilse bir şey yapmasın
    return 1


# bu çöp kutusunu dolu olarak işaretlemek için gereken endpoint fakat sensörle bağlantılı olan bu değil
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