var shapeCar = L.geoJSON(shapecar, {
    onEachFeature: function (feature, layer) {
        layer.bindPopup('<strong> Contours parcelle</strong>')
    },
    style : {
        fillColor: 'grey',
        'fillOpacity': 0.1,
        color:'red'
    }
});

var shapeBf = L.geoJSON(shapebf, {
    onEachFeature: function (feature, layer) {
        layer.bindPopup('<strong> Contours parcelle</strong>')
    },
    style : {
        fillColor: 'grey',
        'fillOpacity': 0.1,
        color:'red'
    }
});

var shapeAdry = L.geoJSON(shapeadry, {
    onEachFeature: function (feature, layer) {
        layer.bindPopup('<strong> Contours parcelle</strong>')
    },
    style : {
        fillColor: 'grey',
        'fillOpacity': 0.1,
        color:'red'
    }
});

var overLayMaps = {
    'SHAPES ' : '',
   // 'ABIDJAN': singleMarker
  }
  




