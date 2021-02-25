rm -rf CovidStatisticsProfileHPSCIrelandOpenData.csv
wget -O CovidStatisticsProfileHPSCIrelandOpenData.csv http://opendata-geohive.hub.arcgis.com/datasets/d8eb52d56273413b84b0187a4e9117be_0.csv

rm -f owid-covid-data.csv.bak
if [ -f owid-covid-data.csv ]; then
   mv owid-covid-data.csv owid-covid-data.csv.bak
fi
rm -rf owid-covid-data.csv
wget https://covid.ourworldindata.org/data/owid-covid-data.csv
