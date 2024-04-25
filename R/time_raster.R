librarian::shelf(
  tidyverse,  sf, pracma
)

pracma::tic()
ruta_shapefile = "./Data/gjson/adm_3.geojson"

ruta_new_raster = "./Data/Raster/settlement/ethiopia_ghs.tif"
ruta_new_raster_masked = "./Data/Raster/settlement/ethiopia_ghs_masked.tif"


raster = terra::rast(ruta_new_raster)
shp_test = sf::st_read(ruta_shapefile)|> arrange(desc(area)) |> slice(1)

shp_test_proj = st_transform(shp_test, st_crs(raster))



terra::extract(raster, shp_test_proj) |> 
  data.frame() |> 
  drop_na() |> 
  as_tibble() |> 
  rename(z = 2) |> 
  count(z)

pracma::toc()
