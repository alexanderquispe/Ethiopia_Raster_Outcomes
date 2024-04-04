library(terra)
library(sf)

ruta_raster = "./Data/Raster/settlement/GHS_BUILT_C_MSZ_E2018_GLOBE_R2022A_54009_10_V1_0.tif"
ruta_shapefile = "./Data/gjson/adm_0.geojson"

ruta_new_raster = "./Data/Raster/settlement/ethiopia_ghs.tif"
ruta_new_raster_masked = "./Data/Raster/settlement/ethiopia_ghs_masked.tif"


shapefile <- st_read(ruta_shapefile)

# raster <- rast(ruta_raster)
# 
# 
# 
# raster_recortado <- crop(raster, shapefile_proyectado)

# writeRaster(raster_recortado, filename = ruta_new_raster, overwrite=T)

# terra::proj

# raster_enmascarado <- mask(raster_recortado, shapefile_proyectado)
# writeRaster(raster_recortado, filename = ruta_new_raster, overwrite=T)

raster <- rast(ruta_new_raster)
shapefile_proyectado <- st_transform(shapefile, crs(raster))

# raster_reprojectado <- project(raster, crs(shapefile))

raster_masked <- terra::mask(raster, shapefile_proyectado)

writeRaster(raster_masked, filename = ruta_new_raster_masked, overwrite = T)
