import requests

raster_pop_url = "https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/maxar_v1/ETH/eth_ppp_2020_constrained.tif"
raster_pop = requests.get(raster_pop_url).content

with open("./Data/Raster/Population/eth_ppp_2020_constrained.tif", "wb") as raster:
    raster.write(raster_pop)

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
