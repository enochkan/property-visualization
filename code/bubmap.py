import overpy
import warnings
warnings.filterwarnings(action='ignore', category=RuntimeWarning)
import pandas as pd
import plotly.plotly as py
import folium
import re
from itertools import chain

def overpyq(loc):
	quer = '''
		area["ISO3166-1"="HK"][admin_level=2];
		(node["name:en"="'''+loc+'''"](area);
		);
		out center;
		'''
	res = api.query(quer)
	return res

#read data
filename='Property price chart _ Midland Realty'
#filename='test'
data = pd.read_csv('./data/'+filename+'.csv', low_memory=False)

#preprocessing
places = []
prices = []
places += [place for place in data.estate]
prices += list(chain.from_iterable(map(int, re.findall(r'\d+',price.replace(',', ''))) for price in data.avg_price_saleable))
querydict = dict(zip(places,prices))

# Collect coords into list
api = overpy.Overpass()
coords  = []
lons = []
lats = []
for key in querydict:
	r = overpyq(str(key))
	if len(r.nodes)==0:
		coords += [(9999,9999)]
	else:
	    coords += [(float(r.nodes[0].lon), float(r.nodes[0].lat))]
lons += [lon[1] for lon in coords]
lats += [lat[0] for lat in coords]

# create dataframe
querydf = pd.DataFrame(querydict.items(), columns=['estate', 'saleable_price'])
querydf['lon'] = lons
querydf['lat'] = lats

#create folium map
m = folium.Map(location=[22.34, 114.1], tiles='cartodbpositron', zoom_start=10.5)
folium.TileLayer('cartodbdark_matter').add_to(m)
folium.TileLayer('stamenterrain').add_to(m)
folium.TileLayer('stamentoner').add_to(m)
folium.LayerControl().add_to(m)
#cartodbpositron
for i in range(0,len(querydf)):
	col = '#FF3333' if querydf.iloc[i]['saleable_price'] > 15000 else ('#FF6633' if querydf.iloc[i]['saleable_price'] > 10000 else '#FF9933')
	folium.Circle(
	  location=[querydf.iloc[i]['lon'], querydf.iloc[i]['lat']],
	  popup=querydf.iloc[i]['estate']+': '+str(querydf.iloc[i]['saleable_price'])+' HKD per sq ft',
	  radius=querydf.iloc[i]['saleable_price']/20,
	  color=col,
	  fill=True,
	  opacity= 0.875,
	  fill_color=col,
	  stroke= True,
	  weight= 1
	).add_to(m)
m.save('hkmap.html')



