import folium
from itertools import chain
import overpy
import re
import warnings
warnings.filterwarnings(action='ignore', category=RuntimeWarning)
import pandas as pd

def overpyq(loc):
	quer = '''
		area["ISO3166-1"="HK"][admin_level=2];
		(node["name:en"="'''+str(loc)+'''"](area);
		);
		out center;
		'''
	res = api.query(quer)
	if not res.nodes:
		quer2 = '''
			area["ISO3166-1"="HK"][admin_level=2];
			(way["name:en"="'''+str(loc)+'''"](area);
			);
			out center;
			'''
		res = api.query(quer2).ways[0].get_nodes(resolve_missing=True)[0] if api.query(quer2).ways != [] else 999
		return res
	res = api.query(quer).nodes[0]
	return res

# read data
filename='Property price chart _ Midland Realty'
#filename='test'
data = pd.read_csv('./data/'+filename+'.csv', low_memory=False)

# preprocessing
places = []
prices = []
places += [place for place in data.estate]
prices += list(chain.from_iterable(map(int, re.findall(r'\d+',price.replace(',', ''))) for price in data.avg_price_saleable))
querydict = dict(zip(places,prices))

# collect coords into list
api = overpy.Overpass()
coords  = []
lons = []
lats = []
for key in querydict:
	r = overpyq(str(key))
	coords += [(float(r.lon), float(r.lat))] if r != 999 else [(float(999), float(999))]
lons += [lon[1] for lon in coords]
lats += [lat[0] for lat in coords]

# create dataframe
querydf = pd.DataFrame(querydict.items(), columns=['estate', 'saleable_price'])
querydf['lon'] = lons
querydf['lat'] = lats

# create folium map
m = folium.Map(location=[22.34, 114.1], tiles='cartodbpositron', zoom_start=10.5)
folium.TileLayer('cartodbdark_matter').add_to(m)
folium.TileLayer('stamenterrain').add_to(m)
folium.TileLayer('stamentoner').add_to(m)
folium.LayerControl().add_to(m)
for i in range(0,len(querydf)):
	col = '#FF0033' if querydf.iloc[i]['saleable_price'] > 15000 else ('#FF6633' if querydf.iloc[i]['saleable_price'] > 10000 else '#FFCC33')
	folium.Circle(
	  location=[querydf.iloc[i]['lon'], querydf.iloc[i]['lat']],
	  popup=querydf.iloc[i]['estate']+': '+str(querydf.iloc[i]['saleable_price'])+' HKD per sq ft',
	  radius=querydf.iloc[i]['saleable_price']/25,
	  color=col,
	  fill=True,
	  opacity= 0.89,
	  fill_color=col,
	  stroke= True,
	  weight= 1
	).add_to(m)
m.save('hkmap.html')



