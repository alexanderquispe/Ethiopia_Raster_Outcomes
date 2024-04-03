import requests

admin = [
    "https://fdw.fews.net/api/feature.geojson?layer=4694",  # adm0
    "https://fdw.fews.net/api/feature.geojson?layer=4695",
    "https://fdw.fews.net/api/feature.geojson?layer=4696",
    "https://fdw.fews.net/api/feature.geojson?layer=4697",
]

adm = list(range(len(admin)))

to = [f"./Data/gjson/adm_{x}.geojson" for x in adm]

# print(to, admin)

for gjson, g_local in zip(admin, to):
    content = requests.get(gjson).content
    with open(g_local, "wb") as f:
        f.write(content)
