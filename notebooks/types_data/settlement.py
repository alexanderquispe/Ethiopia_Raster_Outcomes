import pandas as pd, os

labels = {
    255: "0: NODATA",
    1: "1: MSZ, open spaces, low vegetation surfaces NDVI <= 0.3",
    2: "2: MSZ, open spaces, medium vegetation surfaces 0.3 < NDVI <=0.5",
    3: "3: MSZ, open spaces, high vegetation surfaces NDVI > 0.5",
    4: "4: MSZ, open spaces, water surfaces LAND < 0.5",
    5: "5: MSZ, open spaces, road surfaces",
    11: "11: MSZ, built spaces, residential, building height <= 3m",
    12: "12: MSZ, built spaces, residential, 3m < building height <= 6m",
    13: "13: MSZ, built spaces, residential, 6m < building height <= 15m",
    14: "14: MSZ, built spaces, residential, 15m < building height <= 30m",
    15: "15: MSZ, built spaces, residential, building height > 30m",
    21: "21: MSZ, built spaces, non-residential, building height <= 3m",
    22: "22: MSZ, built spaces, non-residential, 3m < building height <= 6m",
    23: "23: MSZ, built spaces, non-residential, 6m < building height <= 15m",
    24: "24: MSZ, built spaces, non-residential, 15m < building height <= 30m",
    25: "25: MSZ, built spaces, non-residential, building height > 30m",
}


class GHS:
    def __init__(
        self,
        df: pd.DataFrame,
        columns_index=["index", "values", "count"],
        dummy_index="xxyyzz",
        max_value=100,
        drop_columns=["values", "count"],
        prefix="ghs_",
        save_dir: str = None,
        name_files=["ghs_with_na", "ghs_without_na"],
    ):
        self.prefix = prefix
        self.save_dir = save_dir
        self.ref_data = df.drop(columns=drop_columns)
        self.data = df[columns_index]
        self.columns = columns_index
        dummy_val = list(labels.keys())
        self.dummy_index = dummy_index
        self.dummy_df = pd.DataFrame(
            {"values": dummy_val, "index": dummy_index, "percent": 0}
        )
        self.names_files = [name + ".csv" for name in name_files]
        self.max_value = max_value
        self.name_files_dir()

    def gen_percent(self, data: pd.DataFrame):
        cols = self.columns
        count = cols[2]
        result = (
            data.groupby("index")
            .apply(lambda x: x.assign(percent=x[count] / x[count].sum() * 100))
            .drop(columns=[cols[0]])
            .reset_index()
        )
        return result

    def join_dummy(self, data: pd.DataFrame):
        dummy_df = self.dummy_df
        cols = self.columns
        data_with_dummy = pd.concat((data, dummy_df))
        values_cols = data_with_dummy["values"]
        values_cols = [self.prefix + str(int(x)) for x in values_cols]
        data_with_dummy["values"] = values_cols
        result = data_with_dummy.pivot_table(
            index="index", columns="values", values="percent", fill_value=0
        ).reset_index()
        result = result[result[cols[0]] != self.dummy_index]

        return result

    def join_percent(self, data):
        result = self.gen_percent(data)
        result = self.join_dummy(result)
        return result

    def create_dir(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def name_files_dir(self):
        self.create_dir()
        dir = self.save_dir
        files = self.names_files
        self.save_into = [os.path.join(dir, x) for x in files]

    def generate_data(self):
        save_name_files = self.save_into
        cols = self.columns
        drop_na_value = self.max_value
        data = self.data
        data[cols[1]] = data[cols[1]].astype(float)
        max_value = int(max(data[cols[1]]))
        col_drop = self.prefix + str(max_value)
        data_with_na = self.data
        data_with_no_na = data_with_na[data_with_na[cols[1]] < drop_na_value]
        na_result = self.join_percent(data_with_na)
        no_na_result = self.join_percent(data_with_no_na)
        ref_data = self.ref_data
        na_result = pd.merge(ref_data, na_result, on="index").drop_duplicates()
        no_na_result = pd.merge(ref_data, no_na_result, on="index").drop_duplicates()
        na_result.to_csv(save_name_files[0], index=False)
        no_na_result.to_csv(save_name_files[1], index=False)

        self.with_na_result = na_result
        self.without_na_result = no_na_result.drop(columns=[col_drop])
        return self
