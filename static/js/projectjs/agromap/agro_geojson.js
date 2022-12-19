var shapeCar = L.geoJSON(shapecar, {
    onEachFeature: function (feature, layer) {
        layer.bindPopup(`<strong> Contours parcelle</strong>`)
    },
    style : {
        fillColor: 'grey',
        'fillOpacity': 0.1,
        color:'yellow'
    }
});

var shapeBf = L.geoJSON(shapebf, {
    onEachFeature: function (feature, layer) {
        layer.bindPopup(`
        <table class="table table-striped table-bordered">
                <thead style="align-items: center">
                    <tr>
                    <th scope="col" class="center">ID</th>
                    <th scope="col" class="center">INFORMATIONS</th>
                    </tr>
                </thead>
                <tbody style="align-items: center">
                    <tr>
                        <th scope="col"><b>IDENTIFIANT :</b></th>
                        <td class="text-uppercase"><strong>${feature.properties.tident}</strong></td>
                    </tr>
                    <tr>
                    <th scope="col"><b>SUPERFICIE :</b></th>
                    <td class="text-uppercase"><strong>${feature.properties.AREA}</strong></td>
                </tr>
                </tbody>
        </table>
        `)
    },
    style : {
        fillColor: 'grey',
        'fillOpacity': 0.1,
        color:'red'
    }
});

var shapeAdry = L.geoJSON(shapeadry, {
    onEachFeature: function (feature, layer) {
        layer.bindPopup(`
        <table class="table table-striped table-bordered">
                <thead style="align-items: center">
                    <tr>
                    <th scope="col" class="center">ID</th>
                    <th scope="col" class="center">INFORMATIONS</th>
                    </tr>
                </thead>
                <tbody style="align-items: center">
                    <tr>
                        <th scope="col"><b>IDENTIFIANT :</b></th>
                        <td class="text-uppercase"><strong>${feature.properties.tident}</strong></td>
                    </tr>
                    <tr>
                    <th scope="col"><b>SUPERFICIE :</b></th>
                    <td class="text-uppercase"><strong>${feature.properties.AREA}</strong></td>
                </tr>
                </tbody>
        </table>
        `)
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
  




