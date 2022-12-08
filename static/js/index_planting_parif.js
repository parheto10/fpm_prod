const icon = L.icon({
  iconSize: [25, 41],
  iconAnchor: [10, 41],
  popupAnchor: [2, -40],
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png"
});


Promise.all([
  fetch("http://127.0.0.1:8000/api/planting/v1/"),
]).then(async ([response1]) => {

  const responseData1 = await response1.json();

  const data1 = responseData1;
//   console.log(data1);

//   const plantings = L.featureGroup().addTo(map);
  const marker = L.markerClusterGroup();
  const plantings = L.geoJSON();

    data1.forEach(({ code, producteur , latitude, longitude, certification, culture, superficie  }) => {


    plantings.addLayer(
      L.marker([ latitude, longitude], { icon }).bindPopup(
        `
          <table class="table table-striped table-bordered">
            <thead style="align-items: center">
                <tr>
                  <th scope="col" class="center">ID</th>
                  <th scope="col" class="center">INFORMATIONS</th>
                </tr>
            </thead>
            <tbody style="align-items: center">
                <tr>
                    <th scope="col"><b>CODE PARCELLE :</b></th>
                    <td class="text-uppercase"><strong>${code}</strong></td>
                </tr>
                <tr>
                    <th scope="col"><b>PRODUCTEUR :</b></th>
                    <td class="text-uppercase"><strong>${producteur.code} - ${producteur.nom}</strong></td>
                </tr>
                <tr>
                    <th scope="col"><b>LOCALITE :</b></th>
                    <td class="text-uppercase"><strong>${producteur.localite}</strong></td>
                </tr>
                <tr>
                    <th scope="col"><b>COORDONNEES :</b></th>
                    <td class="text-uppercase">(${latitude},${longitude})</td>
                </tr>
                <tr>
                    <th scope="col"><b>CERTIFICATION : </b></th>
                    <td class="text-uppercase">${certification}</td>
                </tr>
                <tr>
                    <th scope="col"><b>CULTURE :</b></th>
                    <td class="text-uppercase">${culture}</td>
                </tr>
                <tr>
                    <th scope="col"><b>SUPERFICIE</b></th>
                    <td class="text-uppercase">${superficie} (Ha)</td>
                </tr>

                <tr>
                    <th scope="col"><b>SUIVIS</b></th>
                    <td class="text-uppercase text-center">
                        <a class="btn btn-default " style="padding: 1px 8px 1px 8px;" href="#" title="voir" onclick="show_planting('http://127.0.0.1:8000/show_planting/${code}')" ><i class="glyphicon glyphicon-eye-open"></i></a>
                    </td>
                </tr>
            </tbody>
          </table>

        `


      )
    );
  });

  plantings.addTo(marker);
  marker.addTo(map);

//  map.fitBounds(plantings.getBounds());
});

//Initialisation de la Map
var map = L.map('map').setView([7.539989, -5.547080], 7);
map.zoomControl.setPosition('topright');

var osm = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
 maxZoom: 26,
 attribution: '@Copyright - AGRO-MAP CI - CARTOGRAPHIE',
 subdomains:['mt0','mt1','mt2','mt3']
}).addTo(map);

var osm1 = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
 maxZoom: 26,
 attribution: '@Copyright - AGRO-MAP CI - CARTOGRAPHIE',
}).addTo(map);

//map Climat
var climat = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
 maxZoom: 26,
 attribution: '@Copyright - AGRO-MAP CI - CARTOGRAPHIE'
});

var osm8 =L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC',
    attribution: '@Copyright - Agro-Map CI - Plantings',
    maxZoom: 26
});

//add Google Map Layer
var googleStreets = L.tileLayer('http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{
    maxZoom: 26,
    attribution: '@Copyright - AGRO-MAP CI - CARTOGRAPHIE',
    subdomains:['mt0','mt1','mt2','mt3']
});

// var googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',{
//     maxZoom: 26,
//     attribution: '@Copyright - AGRO-MAP CI - CARTOGRAPHIE',
//     subdomains:['mt0','mt1','mt2','mt3']
// });

// Ajouter Popup de Marquage
var singleMarker = L.marker([5.349390, -4.017050])
 .bindPopup("Bienvenus en .<br> Côte d'Ivoire.")
 .openPopup();

// Ajouter Calcul de Distance
L.control.scale().addTo(map);

//Afficher les Coordonnées sur la carte
map.on('mousemove', function (e) {
 //console.log(e);
 $('.coordinates').html(`lat: ${e.latlng.lat}, lng: ${e.latlng.lng}`)
});


//Charger les Villes sur la Carte
//L.geoJSON(data).addTo(map);
var marker = L.markerClusterGroup();
marker.addTo(map);

// Laeflet Layer control
var baseMaps = {
 'COUCHE SATELLITE': osm,
 'COUCHE NORMALE': osm1,
 'COUCHE FORESTIERE': climat,
 'COUCHE GOOGLE MAP': googleStreets,
 'COUCHE REGIONALE': osm8,
//  'GOOGLE SATELLITE': googleSat,
}

// var markers = L.markerClusterGroup({
// 	spiderfyShapePositions: function(count, centerPt) {
//         var distanceFromCenter = 35,
//             markerDistance = 45,
//             lineLength = markerDistance * (count - 1),
//             lineStart = centerPt.y - lineLength / 2,
//             res = [],
//             i;

//         res.length = count;

//         for (i = count - 1; i >= 0; i--) {
//             res[i] = new Point(centerPt.x + distanceFromCenter, lineStart + markerDistance * i);
//         }

//         return res;
//     }
// });

// var shapeCargill = L.geoJSON(cargillData).addTo(map);
var shapeCargill = L.geoJSON(cargillData, {
        onEachFeature: function (feature, layer) {
            layer.bindPopup('<strong> Contours parcelle</strong>')
        },
        style : {
            fillColor: 'grey',
            'fillOpacity': 0.1,
            color:'red'
        }
    }).addTo(map);

var overLayMaps = {
  'SHAPES CARGILL' : shapeCargill,
 // 'ABIDJAN': singleMarker
}
L.control.layers(baseMaps, overLayMaps, {collapse :false, position: 'topleft'}).addTo(map);



function show_monitoring(url) {
  event.preventDefault();

  var csrfToken = $('[name="csrfmiddlewaretoken"]').val();

  $.ajax({
      url:url,
      method: "GET",
      dataType : "json",
      success:function(response){

        if(response.status == 400){
          //console.log(response.msg);
          swal({
            title: response.msg,
            icon: "warning",
            //buttons: true,
            dangerMode: true,
          })
        }else{
         // console.log(response.templateStr);
         $('#modal').html(response.templateStr)
         $('#modal').modal('show')

        }


      }
  });


}



function show_espece(url) {
  event.preventDefault();

  var csrfToken = $('[name="csrfmiddlewaretoken"]').val();

  $.ajax({
      url:url,
      method: "GET",
      dataType : "json",
      success:function(response){

        if(response.status == 400){
          //console.log(response.msg);
          swal({
            title: response.msg,
            icon: "warning",
            //buttons: true,
            dangerMode: true,
          })
        }else{
         // console.log(response.templateStr);
         $('#modalEspece').html(response.templateStr)
         $('#modalEspece').modal('show')

        }


      }
  });


}

function show_planting(url){
  event.preventDefault();

  var csrfToken = $('[name="csrfmiddlewaretoken"]').val();

  $.ajax({
      url:url,
      method: "GET",
      dataType : "json",
      success:function(response){

        if(response.status == 400){
          //console.log(response.msg);
          swal({
            title: response.msg,
            icon: "warning",
            //buttons: true,
            dangerMode: true,
          })
        }else{
         // console.log(response.templateStr);
         $('#modal').html(response.templateStr)
         $('#modal').modal('show')

        }

      }
  });
}









