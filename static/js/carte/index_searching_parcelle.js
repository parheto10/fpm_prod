function searchingParcelle(url) {
    event.preventDefault();

    var searchVal = $('#recherche').val();


    if(searchVal != ""){
         // $.blockUI({ message: 'Veuillez patienter traitement en cour...' });
    $.ajax({
        url: url,
        method: "GET",
        data:{
          'code':$('#recherche').val().trim(),
        },
        dataType : "json",
        success:function(response){
         // $.unblockUI();
        if(response.status == 400){
            swal({
                title: response.msg,
                icon: "warning",
                //buttons: true,
                dangerMode: true,
              })
        }else{

            if(response.code != ""){
                $('#map').empty();
                //console.log(response.code);

                document.getElementById('weathermap').innerHTML = "<div id='map' ></div>";
                document.getElementById('map').innerHTML=response.templateStr;

                const icon = L.icon({
                  iconSize: [20, 29],
                  iconAnchor: [10, 41],
                  popupAnchor: [2, -40],
                  iconUrl: "https://unpkg.com/leaflet@1.6/dist/images/marker-icon.png",
                  // iconUrl: "http://127.0.0.1:8000//static/img/icons/my_icon1.png",
                  shadowUrl: "https://unpkg.com/leaflet@1.6/dist/images/marker-shadow.png",
                  // shadowUrl: "http://127.0.0.1:8000//static/img/icons/my_icon1.png"
                });
                Promise.all([
                    fetch("http://127.0.0.1:8000/api/v1/recherche_parcelles/"+response.code),
                  //  fetch("http://127.0.0.1:8000//api/parcelles?format=json")
                  ]).then(async ([response1]) => {
                    const responseData1 = await response1.json();
                    //  const responseData2 = await response2.json();

                      const data1 = responseData1;
                    //  const data2 = responseData2;
                    //console.log(data1);


                      const plantings = L.featureGroup().addTo(map);

                      data1.forEach(({ code,producteur,latitude, longitude, certification, culture, superficie  }) => {


                        plantings.addLayer(
                          L.marker([latitude, longitude], { icon }).bindPopup(
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
                    map.fitBounds(plantings.getBounds());
                  });


                           //Initialisation de la Map
                var map = L.map('map').setView([7.539989, -5.547080], 0);
                map.zoomControl.setPosition('topright');

                var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                 maxZoom: 10,
                 attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors - @Copyright - Agro-Map CI'
                }).addTo(map);

                //map Climat
                var climat = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
                 maxZoom: 22,
                 attribution: '@Copyright - Agro-Map CI - Map'
                });


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
                 'NORMAL': osm,
                 'COUVERT FORESTIER': climat,
                }

                var Parcelles = L.markerClusterGroup({
                  spiderfyShapePositions: function(count, centerPt) {
                        var distanceFromCenter = 35,
                            markerDistance = 45,
                            lineLength = markerDistance * (count - 1),
                            lineStart = centerPt.y - lineLength / 2,
                            res = [],
                            i;

                        res.length = count;

                        for (i = count - 1; i >= 0; i--) {
                            res[i] = new Point(centerPt.x + distanceFromCenter, lineStart + markerDistance * i);
                        }
                        return res;
                    }
                });

                var overLayMaps = {
                 // 'VILLES' : marker,
                 // 'ABIDJAN': singleMarker
                }
                L.control.layers(baseMaps, overLayMaps, {collapse :false, position: 'topleft'}).addTo(map);
                 // Ajouter Mode plein Ecran
                var mapId = document.getElementById('map');
                function fullScreenView(){
                    if(document.fullscreenElement){
                        document.exitFullscreen();
                    } else {
                        mapId.requestFullscreen();
                    }

                }

                //leaflet Browser impression
                L.control.browserPrint({position:'topright'}).addTo(map);

                    //Recherche Leaflet
                    L.Control.geocoder().addTo(map);


                //Ajouter Fonction de Calcul de Distance
                L.control.measure({
                    primaryLengthUnit: 'kilometers',
                    secondaryLengthUnit: 'mètres',
                    primaryAreaUnit: 'hectares',
                    secondaryAreaUnit: 'metres²'
                }).addTo(map);


                    //Retours Acceuil Carte
                $('.zoom').click(function() {
                    map.setView([7.539989, -5.547080], 7);
                });





              }else{

              }

        }




        }
    });

    }else{

    }


}