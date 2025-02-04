# import streamlit as st
# import streamlit.components.v1 as components
# ## แสดง mark ตำแหน่งต่างๆ
# st.title("Maps test")
# def DisplayMap(mark):
#     html_code = f'''
#     <!DOCTYPE HTML>
#     <html>
#         <head>
#             <meta charset="UTF-8">
#             <title>Create Map Sample | Longdo Map</title>
#             <style type="text/css">
#             html{{height:100%;}}
#             body{{margin:0px;height:100%;}}
#             #map {{height: 100%;}}
#             #route {{height: 400px;}}
#             </style>

#             <script type="text/javascript" src="https://api.longdo.com/map/?key=7b6f8a4c53a57fa8315fbdcf5b108c83"></script>
#             <script>
#                 function init() {{
#                     var map = new longdo.Map({{
#                         placeholder: document.getElementById('map')
#                     }});
#                     {mark}
#                 }}
#                 window.onload = init;
#             </script>
#         </head>
#         <body>
#             <div id="map"></div>
#             <div id="route"></div>  <!-- This is the container for displaying route information -->
#         </body>
#     </html>
#     '''
#     components.html(html_code, height=800)

# # JavaScript code with a loop to add markers
# DisplayMap("""
#         var markers = [
#             { lon: 100.56, lat: 13.74, title: 'ร้านหนังสือพิมพ์' },
#             { lon: 100.54, lat: 13.74, title: 'ร้านอีบุค' },
#             { lon: 100.50, lat: 13.74, title: 'กัญนา' }
#         ];

#         for (var i = 0; i < markers.length; i++) {
#             var marker = new longdo.Marker({ lon: markers[i].lon, lat: markers[i].lat }, {title: markers[i].title, detail: '' });
#             map.Overlays.add(marker);
#         }
# """)
 
import streamlit as st
import streamlit.components.v1 as components

# def DisplayMap():
#     html_code = """<!DOCTYPE HTML>
#     <html>
#         <head>
#             <meta charset="UTF-8">
#             <title>Create Map Sample | Longdo Map</title>
#             <style type="text/css">
#             html, body { height: 100%; margin: 0; }
#             #map { height: 100%; }
#             #result {
#                 position: absolute;
#                 top: 0;
#                 bottom: 0;
#                 right: 0;
#                 width: 1px;
#                 height: 80%;
#                 margin: auto;
#                 border: 4px solid #dddddd;
#                 background: #ffffff;
#                 overflow: auto;
#                 z-index: 2;
#             }
#             </style>

#             <script type="text/javascript" src="https://api.longdo.com/map/?key=7b6f8a4c53a57fa8315fbdcf5b108c83"></script>
#             <script type="text/javascript" src="https://code.jquery.com/jquery-1.10.2.min.js"></script>
#             <script>
#                 function init() {
#                     var map = new longdo.Map({
#                         placeholder: document.getElementById('map')
#                     });

#                     // Fetch route first and then add it to the map
#                     longdoMapRouting().then(function(r) {
#                         map.Route.add(r); // Add the route once it's ready
#                     }).catch(function(error) {
#                         console.error("Error adding route to map:", error);
#                     });
#                 }

#                 function longdoMapRouting() {
#                     return fetch("https://api.longdo.com/RouteService/json/route/guide?key=7b6f8a4c53a57fa8315fbdcf5b108c83&flon=100.54898&flat=13.74308&tlon=100.55885&tlat=13.72431")
#                         .then(response => response.json())
#                         .then(results => {
#                             console.log(results);
#                             return results; // Ensure to return the route data
#                         })
#                         .catch(error => {
#                             console.error("Error fetching route:", error);
#                             throw error; // Rethrow the error to be caught later
#                         });
#                 }

#                 window.onload = init;
#             </script>
#         </head>
#         <body>
#             <div id="map"></div>
#         </body>
#     </html>"""

#     components.html(html_code, height=800)

# DisplayMap()


# map.Route.placeholder(document.getElementById('result'));
# map.Route.add(new longdo.Marker({ lon: 100.538316, lat: 13.764953 },
#     { 
#         title: 'Victory monument', 
#         detail: 'I\'m here' 
#     }
# ))
# map.Route.add({ lon: 100, lat: 15 })
# map.Route.search()


def DisplayMap():
    html_code = """<!DOCTYPE HTML>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Create Map Sample | Longdo Map</title>
        <style type="text/css">
        html, body { height: 100%; margin: 0; }
        #map { height: 80%; width: 100%; }
        #result {
            width: 100%;
            height: 20%;
            background: #ffffff;
            border-top: 4px solid #dddddd;
            overflow: auto;
            padding: 10px;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }
        </style>

        <script type="text/javascript" src="https://api.longdo.com/map/?key=7b6f8a4c53a57fa8315fbdcf5b108c83"></script>
        <script type="text/javascript" src="https://code.jquery.com/jquery-1.10.2.min.js"></script>
        <script>
            function init() {
                var map = new longdo.Map({
                    placeholder: document.getElementById('map')
                });

                // Set initial map location and zoom level
                map.location({ lon: 100.54898, lat: 13.74308 }, 14);

                // Define route mode
                map.Route.mode(longdo.RouteMode.Cost); // Set route mode to 'Cost'

                // Create markers for start and end points
                var startMarker = new longdo.Marker({ lon: 100.54898, lat: 13.74308 });
                var endMarker = new longdo.Marker({ lon: 100.55885, lat: 13.72431 });

                // Add markers to the map
                map.addMarker(startMarker);
                map.addMarker(endMarker);

                // Set route between start and end points
                map.Route.add({ lon: 100.54898, lat: 13.74308 }); // Starting point
                map.Route.add({ lon: 100.55885, lat: 13.72431 }); // End point

                // Search for the route and display result
                map.Route.search().then(function(result) {
                    console.log(result); // Handle result after searching for the route
                    // Once route is found, it will display on the map
                    if(result && result.routes && result.routes.length > 0) {
                        displayRouteDetails(result.routes[0]); // Display route details
                    }
                }).catch(function(error) {
                    console.error("Error searching for route:", error);
                });

                // Fetch route details and display them
                longdoMapRouting().then(function(r) {
                    map.Route.add(r); // Add the route once it's ready
                    displayRouteDetails(r); // Display details
                }).catch(function(error) {
                    console.error("Error adding route to map:", error);
                });
            }

            function longdoMapRouting() {
                return fetch("https://api.longdo.com/RouteService/json/route/guide?key=7b6f8a4c53a57fa8315fbdcf5b108c83&flon=100.54898&flat=13.74308&tlon=100.55885&tlat=13.72431")
                    .then(response => response.json())
                    .then(results => {
                        console.log(results);
                        return results; // Ensure to return the route data
                    })
                    .catch(error => {
                        console.error("Error fetching route:", error);
                        throw error; // Rethrow the error to be caught later
                    });
            }

            function displayRouteDetails(routeData) {
                var resultDiv = document.getElementById('result');
                resultDiv.innerHTML = ''; // Clear any existing content

                // Check if route data exists and display it
                if (routeData && routeData.routes && routeData.routes.length > 0) {
                    var route = routeData.routes[0];
                    var details = `
                        <h3>Route Details</h3>
                        <p><strong>Start Point:</strong> ${route.start.lat}, ${route.start.lon}</p>
                        <p><strong>End Point:</strong> ${route.end.lat}, ${route.end.lon}</p>
                        <p><strong>Distance:</strong> ${route.distance} meters</p>
                        <p><strong>Duration:</strong> ${route.duration} seconds</p>
                    `;
                    resultDiv.innerHTML = details;
                } else {
                    resultDiv.innerHTML = '<p>No route data available.</p>';
                }
            }

            window.onload = init;
        </script>
    </head>
    <body>
        <div id="map"></div>
        <div id="result"></div> <!-- This is where the route details will be shown -->
    </body>
</html>
"""

    components.html(html_code, height=800)

DisplayMap()
