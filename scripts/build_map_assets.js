const fs = require('fs');
const topojson = require('topojson-client');
const world = require('world-atlas/countries-110m.json');
const geo = topojson.feature(world, world.objects.countries);
fs.mkdirSync('map-assets', {recursive:true});
fs.writeFileSync('map-assets/countries.geojson', JSON.stringify(geo));
