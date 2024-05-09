import requests
from app import convertBins


token = "pk.eyJ1IjoibGVyaXRoIiwiYSI6ImNsdnIyZmh6cDBnZXYya21oZGFxendvcWsifQ.Qhm_zr1bKU_Jkuk8HSr80w"


def calculateGraph(data_list):
    
    directions_list = []
    for i in range(len(data_list)):
        for j in range(len(data_list)):

            #  token değişebilir daha sonrasında burayı da dinamik yapabiliriz.
            response = requests.get(f'https://api.mapbox.com/directions/v5/mapbox/driving/{data_list[i]["bin_lat"]},{data_list[i]["bin_lng"]};{data_list[j]["bin_lat"]},{data_list[j]["bin_lng"]}?steps=true&geometries=geojson&access_token={token}')
            if response.status_code == 200:
                directions_list.append(response.json())
            else:
                # tek bir noktada bile hata alınırsa matris bozulur o yüzden direkt döngü durduruabilir.
                print(f"Error: {response.status_code}, {response.text}")

    matrix = [[0 for _ in range(len(data_list))] for _ in range(len(data_list))]
    index = 0
    for i in range(len(data_list)):
        for j in range(len(data_list)):
            matrix[i][j] = directions_list[index]["routes"][0]["duration"]
            index += 1

    return matrix