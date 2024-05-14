from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from route import calculateGraph
from route import djikstra




ALLOWED_ORIGIN = 'http://localhost:5173'

app = Flask(__name__)

CORS(app,origins=ALLOWED_ORIGIN)


uri = "mongodb+srv://ozgurokanozdal:okanokan1@bincluester.0iydmxy.mongodb.net/"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["waste_management"]


# areaCode a göre bütün çöp kutularını döner
@app.route('/api/v1/gel-all/<areaCode>', methods = ["GET"])
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
@app.route('/api/v1/get-all-full/<areaCode>', methods = ["GET"])
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
@app.route('/api/v1/optimum-route/<areaCode>', methods = ["GET"])
def getRouteByAreaCode(areaCode):
    try:
        col = db["bins"]
        colGraph = db["graph"]
        bins_full =convertBins(col.find({"bin_area_code" : int(areaCode), "is_full" : 1}))
        graph_from_db = colGraph.find_one({"graph_area_code" : int(areaCode)})
        
        if (graph_from_db is not None):
            graph_for_djikstra = graph_from_db["graph"]
            g = djikstra.Graph(len(graph_for_djikstra))
            g.graph = graph_for_djikstra
            route = list()
            spesific_nodes = [bin["index_field"] for bin in bins_full]
            source_node = 19
            route = []
            while spesific_nodes:
                distances, parent = g.dijkstra(source_node)
                min_distance_node = min(spesific_nodes, key=lambda node: distances[node])
                path = g.printPath(parent, min_distance_node)
                route.extend(path)
                spesific_nodes.remove(min_distance_node)
                source_node = min_distance_node

            unique_route = []
            prev_node = None
            for node in route:
                if node != prev_node:
                    unique_route.append(node)
                prev_node = node
            
            bin_route = list()

            for bin_index in unique_route:
                temp = col.find_one({"index_field" : bin_index})
                bin_route.append(temp)
            return convertBins(bin_route)
        else:
            return jsonify({"error" : "There is no graph information for this area"}), 404
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


@app.route("/api/v1/create-graph/<areaCode>", methods = ["POST"])
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
                ids[str(i)] = bins[i]["id"]
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



@app.route("/api/v1/update-graph/<areaCode>", methods=["UPDATE"])
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
        return None
    else:
        return jsonify({"error" : "Graph not found"}),404
   

#  kutuyu alındı olarak işaretlendikten sonra dbde is_full'u boşaltacak endpoint 
# rota da her sonraki dendiğinde bu endpointe update atılacak
@app.route("/api/v1/discharge/<binId>", methods = ["UPDATE"])
def dischargeBinByBinId(binId):
    col = db["bins"]
    bin = col.find_one({"_id" : str(binId)})
    if bin:
        col.update_one({"_id" : str(binId)} , {"is_full" : 0})
        return jsonify({"success" : "bin discharge succesfully"}),200
    else:
        return jsonify({"error" : "bin not found id" + str(binId)}),404

# bu çöp kutusunu dolu olarak işaretlemek için gereken endpoint fakat sensörle bağlantılı olan bu değil
@app.route("/api/v1/fill/<binId>", methods = ["UPDATE"])
def fillBinByBinId(binId):
    col = db["bins"]
    bin = col.find_one({"_id" : str(binId)})
    if bin:
        col.update_one({"_id" : str(binId)} , {"is_full" : 1})
        return jsonify({"success" : "bin fill succesfully"}),200
    else:
        return jsonify({"error" : "bin not found id" + str(binId)}),404



def convertBins(data):
    data_list = []

    for item in data:
        data_dict = {
            "id" : str(item["_id"]),
            "index_field" : int(item["index_field"]),
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