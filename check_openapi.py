import json


with open("openapi.json", "r", encoding="utf-8") as file:
    data = json.load(file)


print("JSON格式正确")
print("接口标题：", data["info"]["title"])
print("接口路径：", list(data["paths"].keys()))