import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = gpd.read_file("./trips.csv", encoding="utf-8")
print(df.head()) 

count = 0
total = 100000000

# while count < total:

df['origin_coord'] = gpd.GeoSeries.from_wkt(df['origin_coord'])
df['destination_coord'] = gpd.GeoSeries.from_wkt(df['destination_coord'])
df = df.drop(columns=["geometry"])
df = df.drop_index()

print(df.dtypes)
print(df.head())