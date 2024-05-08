import requests
from app import exportData

token = "pk.eyJ1IjoibGVyaXRoIiwiYSI6ImNsdnIyZmh6cDBnZXYya21oZGFxendvcWsifQ.Qhm_zr1bKU_Jkuk8HSr80w"

client = exportData()
db = client["waste_management"]
col = db["bins"]

data_list = []
for item in col.find():
    data_dict = {
        "id": str(item["_id"]),
        "bin_lng": item["bin_lng"],
        "bin_lat": item["bin_lat"],
        "bin_location_str": item["bin_location_str"],
        "bin_area_code": item["bin_area_code"],
        "bin_type_id": item["bin_type_id"],
        "is_full": item["is_full"]
    }
    data_list.append(data_dict)

directions_list = []
for i in range(len(data_list)):
    for j in range(len(data_list)):
        response = requests.get(f'https://api.mapbox.com/directions/v5/mapbox/driving/{data_list[i]["bin_lat"]},{data_list[i]["bin_lng"]};{data_list[j]["bin_lat"]},{data_list[j]["bin_lng"]}?steps=true&geometries=geojson&access_token={token}')
        if response.status_code == 200:
            directions_list.append(response.json())
        else:
            print(f"Error: {response.status_code}, {response.text}")


for a in directions_list:
    print(a["routes"][0]["duration"])

matrix = [[0 for _ in range(len(data_list))] for _ in range(len(data_list))]
index = 0
for i in range(len(data_list)):
    for j in range(len(data_list)):
        matrix[i][j] = directions_list[index]["routes"][0]["duration"]
        index += 1
        
for row in matrix:
    print(row)