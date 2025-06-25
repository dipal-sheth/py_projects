import urllib3
import json

http = urllib3.PoolManager()

url = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"

response = http.request("GET", url)

if response.status == 200:
    data = json.loads(response.data.decode("utf-8"))  
    records = data.get("data", [])  
    
    with open("src\rearc\data\population_data.jsonl", "w") as outfile:
        for record in records:
            json.dump(record, outfile)
            outfile.write("\n")
    
    print("Data successfully written to population_data.json")
else:
    print(f"Request failed with status code {response.status}")
