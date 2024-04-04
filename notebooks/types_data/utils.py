import geopandas as gpd
import pandas as pd, numpy as np
import rasterio as rio, os

import warnings, time

warnings.filterwarnings("ignore")

from tqdm import tqdm
from rasterio.mask import mask


class RasterIOInd:
    def __init__(
        self,
        path_tiff: str,
        shp_gdf: gpd.GeoDataFrame,
        metric_name: str,
        save_result_csv: str = None,
        cols_dataref=["admin_0", "admin_1", "admin_2", "admin_3"],
        metrics=[np.mean, np.std, np.sum],
        only_metric=False,
    ) -> None:
        self.raster = path_tiff
        self.name = metric_name
        self.cols_ref = cols_dataref
        self.metrics = metrics
        self.gdf = shp_gdf
        self.only_metric = only_metric
        self.save = save_result_csv
        with rio.open(path_tiff) as raster:
            self.crs = raster.crs.to_dict()

    def _raster_to_data(self, raster_cropped, transformation) -> np.array:
        values = raster_cropped.flatten()
        rows, cols = np.indices(raster_cropped.shape[-2:])
        x, y = rio.transform.xy(transformation, rows.flatten(), cols.flatten())
        data = {"x": x, "y": y, "z": values}
        df = pd.DataFrame(data).query("z>0").dropna()
        stats = df["z"].agg(self.metrics).values.flatten()
        return stats

    def _metric_values(self, raster_cropped) -> np.array:
        values = np.array(raster_cropped.flatten()).astype(float)
        values = values[~np.isnan(values)]
        values = values[values > 0]
        metrics = self.metrics
        stats = [metric(values) for metric in metrics]

        return stats

    def get_data_raster_shapefile(self, row: int) -> pd.DataFrame:
        crs = self.crs
        row_gdf = self.gdf.iloc[row : row + 1].to_crs(crs)
        row_gdf_out = row_gdf[self.cols_ref]

        with rio.open(self.raster) as raster:
            raster_cropped, transformation = mask(raster, row_gdf.geometry, crop=True)

        if self.only_metric:
            stats = self._metric_values(raster_cropped)
        else:
            stats = self._raster_to_data(raster_cropped, transformation)

        new_col_name = self.name

        (
            row_gdf_out[f"{new_col_name}_mean"],
            row_gdf_out[f"{new_col_name}_sd"],
            row_gdf_out[f"{new_col_name}_sum"],
        ) = stats

        return row_gdf_out

    def create_dir(self):
        split_path = self.save.split("/")
        dir_value = split_path[: len(split_path) - 1]
        dir_name = "/".join(dir_value)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def get_result(self):
        begin_time = time.time()
        total_rows = len(self.gdf)
        result_df = pd.DataFrame()

        for row in tqdm(range(total_rows)):
            result_row = self.get_data_raster_shapefile(row)
            result_df = pd.concat((result_df, result_row))
        end_time = time.time()

        self.result_df = result_df
        save = self.save
        if save is not None:
            self.create_dir()
            result_df.to_csv(save, index=False)

        self.total_time = end_time - begin_time
        return self
