## การทำbook mark หลายๆที่
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
 
 
# import streamlit as st
# import streamlit.components.v1 as components

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


# # map.Route.placeholder(document.getElementById('result'));
# # map.Route.add(new longdo.Marker({ lon: 100.538316, lat: 13.764953 },
# #     { 
# #         title: 'Victory monument', 
# #         detail: 'I\'m here' 
# #     }
# # ))
# # map.Route.add({ lon: 100, lat: 15 })
# # map.Route.search()


# # เส้นทางในการเดินทางในแผนที่
# import streamlit as st
# import streamlit.components.v1 as components

# def DisplayMap():
#     html_code = """<!DOCTYPE HTML>
# <html>
#     <head>
#         <meta charset="UTF-8">
#         <title>Create Map Sample | Longdo Map</title>
#         <style type="text/css">
#         html, body { height: 100%; margin: 0; }
#         #map { height: 80%; width: 100%; }
#         #result {
#             width: 100%;
#             height: 20%;
#             background: #ffffff;
#             border-top: 4px solid #dddddd;
#             overflow: auto;
#             padding: 10px;
#             box-sizing: border-box;
#             font-family: Arial, sans-serif;
#         }
#         </style>
#         <script type="text/javascript" src="https://api.longdo.com/map/?key=7b6f8a4c53a57fa8315fbdcf5b108c83"></script>
#     </head>
#     <body>
#         <div id="map"></div>
#         <div id="result"></div>

#         <script>
#             function init() {
#                 var map = new longdo.Map({
#                     placeholder: document.getElementById('map')
#                 });

#                 map.location({ lon: 100.54898, lat: 13.74308 }, 14);
#                 map.Route.mode(longdo.RouteMode.Cost);

#                 var startMarker = new longdo.Marker({ lon: 100.54898, lat: 13.74308 });
#                 var endMarker = new longdo.Marker({ lon: 100.55885, lat: 13.72431 });

#                 map.Overlays.add(startMarker);
#                 map.Overlays.add(endMarker);

#                 map.Route.add({ lon: 100.54898, lat: 13.74308 });
#                 map.Route.add({ lon: 100.55885, lat: 13.72431 });

#                 map.Route.search().then(function(result) {
#                     if (result && result.routes && result.routes.length > 0) {
#                         displayRouteDetails(result.routes[0]);
#                     }
#                 }).catch(function(error) {
#                     console.error("Error searching for route:", error);
#                 });
#             }

#             function displayRouteDetails(routeData) {
#                 var resultDiv = document.getElementById('result');
#                 resultDiv.innerHTML = '';

#                 if (routeData) {
#                     var details = `
#                         <h3>Route Details</h3>
#                         <p><strong>Distance:</strong> ${routeData.distance} meters</p>
#                         <p><strong>Duration:</strong> ${routeData.duration} seconds</p>
#                     `;
#                     resultDiv.innerHTML = details;
#                 } else {
#                     resultDiv.innerHTML = '<p>No route data available.</p>';
#                 }
#             }

#             // ใช้ setTimeout เพื่อให้แน่ใจว่า API โหลดเสร็จก่อนเรียก init()
#             setTimeout(function() {
#                 if (typeof longdo !== "undefined") {
#                     init();
#                 } else {
#                     console.error("Longdo Map API failed to load.");
#                 }
#             }, 1000);
#         </script>
#     </body>
# </html>
# """
#     components.html(html_code, height=800)

# st.title("Longdo Map in Streamlit")
# DisplayMap()

# import streamlit as st
# import streamlit.components.v1 as components
# def DisplayMap():
#     html_code = """<!DOCTYPE HTML>
# <html>
#     <head>
#         <meta charset="UTF-8">
#         <title>Create Map Sample | Longdo Map</title>
#         <style type="text/css">
#         html, body { height: 100%; margin: 0; }
#         #map { height: 80%; width: 100%; }
#         #result {
#             width: 100%;
#             height: 20%;
#             background: #ffffff;
#             border-top: 4px solid #dddddd;
#             overflow: auto;
#             padding: 10px;
#             box-sizing: border-box;
#             font-family: Arial, sans-serif;
#         }
#         </style>
#         <script type="text/javascript" src="https://api.longdo.com/map/?key=7b6f8a4c53a57fa8315fbdcf5b108c83"></script>
#     </head>
#     <body>
#         <div id="map"></div>
#         <div id="result"></div>

#         <script>
#             function init() {
#                 var map = new longdo.Map({
#                     placeholder: document.getElementById('map')
#                 });

#                 map.location({ lon: 100.54898, lat: 13.74308 }, 14);
#                 map.Route.mode(longdo.RouteMode.Cost);

#                 var startMarker = new longdo.Marker({ lon: 100.54898, lat: 13.74308 });
#                 var endMarker = new longdo.Marker({ lon: 100.55885, lat: 13.72431 });

#                 map.Overlays.add(startMarker);
#                 map.Overlays.add(endMarker);

#                 map.Route.add({ lon: 100.54898, lat: 13.74308 });
#                 map.Route.add({ lon: 100.55885, lat: 13.72431 });

#                 map.Route.search().then(function(result) {
#                     if (result && result.routes && result.routes.length > 0) {
#                         displayRouteDetails(result.routes[0]);
#                     }
#                 }).catch(function(error) {
#                     console.error("Error searching for route:", error);
#                 });

#                 // เรียก API เพื่อดึงข้อมูลเส้นทาง
#                 fetchRouteDetails();
#             }

#             function fetchRouteDetails() {
#                 fetch("https://api.longdo.com/RouteService/json/route/guide?key=7b6f8a4c53a57fa8315fbdcf5b108c83&flon=100.54898&flat=13.74308&tlon=100.55885&tlat=13.72431")
#                     .then(response => response.json())
#                     .then(data => {
#                         console.log("Route details:", data);
#                         displayStepByStep(data);
#                     })
#                     .catch(error => {
#                         console.error("Error fetching route details:", error);
#                     });
#             }

#             function displayRouteDetails(routeData) {
#                 var resultDiv = document.getElementById('result');
#                 resultDiv.innerHTML = '';

#                 if (routeData) {
#                     var details = `
#                         <h3>Route Summary</h3>
#                         <p><strong>Distance:</strong> ${routeData.distance} meters</p>
#                         <p><strong>Duration:</strong> ${routeData.duration} seconds</p>
#                     `;
#                     resultDiv.innerHTML = details;
#                 } else {
#                     resultDiv.innerHTML = '<p>No route data available.</p>';
#                 }
#             }

#             function displayStepByStep(routeData) {
#                 var resultDiv = document.getElementById('result');
#                 if (!routeData || !routeData.routes || routeData.routes.length === 0) {
#                     resultDiv.innerHTML += "<p>No detailed route information available.</p>";
#                     return;
#                 }

#                 var steps = routeData.routes[0].guide;
#                 var stepDetails = "<h3>Turn-by-Turn Directions</h3><ul>";

#                 steps.forEach((step, index) => {
#                     stepDetails += `<li><strong>Step ${index + 1}:</strong> ${step.text} (${step.distance} meters)</li>`;
#                 });

#                 stepDetails += "</ul>";
#                 resultDiv.innerHTML += stepDetails;
#             }

#             // ใช้ setTimeout เพื่อให้ API โหลดเสร็จก่อนเรียก init()
#             setTimeout(function() {
#                 if (typeof longdo !== "undefined") {
#                     init();
#                 } else {
#                     console.error("Longdo Map API failed to load.");
#                 }
#             }, 1000);
#         </script>
#     </body>
# </html>
# """
#     components.html(html_code, height=800)

# st.title("Longdo Map - Turn-by-Turn Directions")
# DisplayMap()


## มีการทำงานของการเพิ่มหลายจุดและมีเส้นทางของการเดินทาง
# import streamlit as st
# import streamlit.components.v1 as components

# st.title("Maps test")

# def DisplayMap():
#     html_code = """<!DOCTYPE HTML>
#     <html>
#         <head>
#             <meta charset="UTF-8">
#             <title>Longdo Map Route</title>
#             <style type="text/css">
#             html, body { height: 100%; margin: 0; }
#             #map { height: 80%; width: 100%; }
#             #result {
#                 width: 100%;
#                 height: 20%;
#                 background: #ffffff;
#                 border-top: 4px solid #dddddd;
#                 overflow: auto;
#                 padding: 10px;
#                 box-sizing: border-box;
#                 font-family: Arial, sans-serif;
#             }
#             </style>
#             <script type="text/javascript" src="https://api.longdo.com/map/?key=7b6f8a4c53a57fa8315fbdcf5b108c83"></script>
#         </head>
#         <body>
#             <div id="map"></div>
#             <div id="result"></div>

#             <script>
#                 function init() {
#                     var map = new longdo.Map({
#                         placeholder: document.getElementById('map')
#                     });

#                     map.location({ lon: 100.54898, lat: 13.74308 }, 14);
#                     map.Route.mode(longdo.RouteMode.Cost);  // ใช้โหมดคำนวณค่าใช้จ่าย

#                     var locations = [
#                         { lon: 100.54898, lat: 13.74308, title: 'จุดเริ่มต้น' },
#                         { lon: 100.54, lat: 13.74, title: 'ร้านอีบุค' },
#                         { lon: 100.50, lat: 13.74, title: 'กัญนา' },
#                         { lon: 100.55885, lat: 13.72431, title: 'จุดปลายทาง' }
#                     ];

#                     // วางหมุดบนแผนที่
#                     for (var i = 0; i < locations.length; i++) {
#                         var marker = new longdo.Marker(
#                             { lon: locations[i].lon, lat: locations[i].lat },
#                             { title: locations[i].title }
#                         );
#                         map.Overlays.add(marker);
#                         map.Route.add({ lon: locations[i].lon, lat: locations[i].lat });
#                     }

#                     // ค้นหาเส้นทาง
#                     map.Route.search().then(function(result) {
#                         if (result && result.routes && result.routes.length > 0) {
#                             displayRouteDetails(result.routes[0]);
#                         }
#                     }).catch(function(error) {
#                         console.error("Error searching for route:", error);
#                     });
#                 }

#                 function displayRouteDetails(routeData) {
#                     var resultDiv = document.getElementById('result');
#                     resultDiv.innerHTML = '';

#                     if (routeData) {
#                         var details = `
#                             <h3>Route Details</h3>
#                             <p><strong>Distance:</strong> ${routeData.distance} meters</p>
#                             <p><strong>Duration:</strong> ${routeData.duration} seconds</p>
#                         `;
#                         resultDiv.innerHTML = details;
#                     } else {
#                         resultDiv.innerHTML = '<p>No route data available.</p>';
#                     }
#                 }

#                 setTimeout(function() {
#                     if (typeof longdo !== "undefined") {
#                         init();
#                     } else {
#                         console.error("Longdo Map API failed to load.");
#                     }
#                 }, 1000);
#             </script>
#         </body>
#     </html>
#     """
#     components.html(html_code, height=800)

# DisplayMap()


import streamlit as st
import streamlit.components.v1 as components
import json

st.title("Longdo Map - Route & POIs")

def DisplayMap(poi_markers_js, route_markers_js):
    html_code = f"""
    <!DOCTYPE HTML>
    <html>
        <head>
            <meta charset="UTF-8">
            <title>Longdo Map Route</title>
            <style type="text/css">
            html, body {{ height: 100%; margin: 0; }}
            #map {{ height: 80%; width: 100%; }}
            
            </style>
            <script type="text/javascript" src="https://api.longdo.com/map/?key=7b6f8a4c53a57fa8315fbdcf5b108c83"></script>
        </head>
        <body>
            <div id="map"></div>
            <div id="result"></div>

            <script>
                function init() {{
                    var map = new longdo.Map({{
                        placeholder: document.getElementById('map')
                    }});

                    map.Route.mode(longdo.RouteMode.Cost);

                    var poiMarkers = {poi_markers_js};
                    var routeMarkers = {route_markers_js};

                    // วางหมุดสำหรับสถานที่น่าสนใจ (POI)
                    for (var i = 0; i < poiMarkers.length; i++) {{
                        var marker = new longdo.Marker(
                            {{ lon: poiMarkers[i].lon, lat: poiMarkers[i].lat }},
                            {{ title: poiMarkers[i].title, icon: {{ url: "https://map.longdo.com/mmmap/images/pin_mark.png", offset: {{ "x": 12, "y": 35 }} }} }}
                        );
                        map.Overlays.add(marker);
                    }}

                    // วางหมุดต้นทาง-ปลายทาง + คำนวณเส้นทาง
                    for (var i = 0; i < routeMarkers.length; i++) {{
                        var marker = new longdo.Marker(
                            {{ lon: routeMarkers[i].lon, lat: routeMarkers[i].lat }},
                            {{ title: routeMarkers[i].title, icon: {{ url: "https://map.longdo.com/mmmap/images/pin_red.png", offset: {{ "x": 12, "y": 35 }} }} }}
                        );
                        map.Overlays.add(marker);
                        map.Route.add({{ lon: routeMarkers[i].lon, lat: routeMarkers[i].lat }});
                    }}

                    // ค้นหาเส้นทางและแสดงผล
                    map.Route.search().then(function(result) {{
                        if (result && result.routes && result.routes.length > 0) {{
                            displayRouteDetails(result.routes[0]);
                        }} else {{
                            console.error("No route data available.");
                        }}
                    }}).catch(function(error) {{
                        console.error("Error searching for route:", error);
                    }});
                }}

                function displayRouteDetails(routeData) {{
                    var resultDiv = document.getElementById('result');
                    resultDiv.innerHTML = '';

                    if (routeData && routeData.summary) {{
                        var details = `
                            <h3>Route Details</h3>
                            <p><strong>Distance:</strong> ${{routeData.summary.distance}} meters</p>
                            <p><strong>Duration:</strong> ${{routeData.summary.duration}} seconds</p>
                        `;
                        resultDiv.innerHTML = details;
                    }} else {{
                        resultDiv.innerHTML = '<p>No route data available.</p>';
                    }}
                }}

                setTimeout(function() {{
                    if (typeof longdo !== "undefined") {{
                        init();
                    }} else {{
                        console.error("Longdo Map API failed to load.");
                    }}
                }}, 1000);
            </script>
        </body>
    </html>
    """
    components.html(html_code, height=800)

# 🔥 ข้อมูลที่แยกเป็น 2 ประเภท
poi_markers = [
    { "lon": 100.551857, "lat": 13.742574, "title": "ร้านหนังสือพิมพ์" },
    { "lon": 100.501796692173, "lat": 13.7558635299692, "title": "ร้านอาหารหรรษายอดผัก" },
    { "lon": 100.501392917058, "lat": 13.7553115354796, "title": "ร้านอาหารชิคเค่นทรีท" },
    { "lon": 100.50142830701398, "lat": 13.755223794845131, "title": "ร้านอาหารนะโม คิทเช่น" },
    { "lon": 100.50520420074463, "lat": 13.759779743332523,"title":"ร้านอาหาร บราวน์ชูการ์ พระสุเมรุ"},
    { "lon": 100.508751408176, "lat": 13.7612783972825,"title":"ร้านอาหาร บราวน์ชูการ์ พระสุเมรุ"},
    { "lon": 100.504047076624, "lat": 13.7599914917184,"title":"ร้านอาหารร้าน ป. โภชนา"} 
]

 
route_markers = [
    { "lon": 100.5018, "lat": 13.7563, "title": "จุดเริ่มต้น"  },
 
    { "lon": 99.978337, "lat": 14.022788, "title": "จุดปลายทาง" }
]

# แปลง Python List -> JSON string ให้ JavaScript ใช้
poi_markers_js = json.dumps(poi_markers, ensure_ascii=False)
route_markers_js = json.dumps(route_markers, ensure_ascii=False)

DisplayMap(poi_markers_js, route_markers_js)


import streamlit as st
import streamlit.components.v1 as components
import json

st.title("Longdo Map - Route & POIs")

def DisplayMap(poi_markers_js, route_markers_js):
    html_code = f"""
   <!DOCTYPE HTML>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Longdo Map Route</title>
        <style type="text/css">
        html, body {{ height: 100%; margin: 0; }}
        #map {{ height: 100%; width: 100%; }}
        </style>
        <script type="text/javascript" src="https://api.longdo.com/map/?key=7b6f8a4c53a57fa8315fbdcf5b108c83"></script>
    </head>
    <body>
        <div id="map"></div>

        <script>
            function init() {{
                var map = new longdo.Map({{
                    placeholder: document.getElementById('map')
                }});

                map.Route.mode(longdo.RouteMode.Cost);

                var poiMarkers = {poi_markers_js};
                var routeMarkers = {route_markers_js};

                // วางหมุดสำหรับสถานที่น่าสนใจ (POI)
                for (var i = 0; i < poiMarkers.length; i++) {{
                    var marker = new longdo.Marker(
                        {{ lon: poiMarkers[i].lon, lat: poiMarkers[i].lat }},
                        {{ title: poiMarkers[i].title, icon: {{ url: "https://map.longdo.com/mmmap/images/pin_mark.png", offset: {{ "x": 12, "y": 35 }} }} }}
                    );
                    map.Overlays.add(marker);
                }}

                // วางหมุดต้นทาง-ปลายทาง + คำนวณเส้นทาง
                for (var i = 0; i < routeMarkers.length; i++) {{
                    var marker = new longdo.Marker(
                        {{ lon: routeMarkers[i].lon, lat: routeMarkers[i].lat }},
                        {{ title: routeMarkers[i].title, icon: {{ url: "https://map.longdo.com/mmmap/images/pin_red.png", offset: {{ "x": 12, "y": 35 }} }} }}
                    );
                    map.Overlays.add(marker);
                    map.Route.add({{ lon: routeMarkers[i].lon, lat: routeMarkers[i].lat }});
                }}

                // ค้นหาเส้นทางและแสดงผล
                map.Route.search().then(function(result) {{
                    if (result && result.routes && result.routes.length > 0) {{
                        console.log("Route found: ", result.routes[0]);
                    }} else {{
                        console.error("No route data available.");
                    }}
                }}).catch(function(error) {{
                    console.error("Error searching for route:", error);
                }});
            }}

            setTimeout(function() {{
                if (typeof longdo !== "undefined") {{
                    init();
                }} else {{
                    console.error("Longdo Map API failed to load.");
                }}
            }}, 1000);
        </script>
    </body>
</html>

    """
    components.html(html_code, height=800)

# 🔥 ข้อมูลที่แยกเป็น 2 ประเภท
poi_markers = [
    { "lon": 100.501796692173, "lat": 13.7558635299692, "title": "ร้านอาหารหรรษายอดผัก" },
    { "lon": 100.501392917058, "lat": 13.7553115354796, "title": "ร้านอาหารชิคเค่นทรีท" },
    { "lon": 100.50142830701398, "lat": 13.755223794845131, "title": "ร้านอาหารนะโม คิทเช่น" },
    { "lon": 100.50520420074463, "lat": 13.759779743332523,"title":"ร้านอาหาร บราวน์ชูการ์ พระสุเมรุ"},
    { "lon": 100.508751408176, "lat": 13.7612783972825,"title":"ร้านอาหาร บราวน์ชูการ์ พระสุเมรุ"},
    { "lon": 100.504047076624, "lat": 13.7599914917184,"title":"ร้านอาหารร้าน ป. โภชนา"}
]

routeMarkers = [
    { "lon": 100.5018, "lat": 13.7563, "title": "จุดเริ่มต้น", "distance": 0, "interval": 0 },
    { "distance": 39, "interval": 14 },
    { "distance": 135, "interval": 46 },
    { "distance": 55, "interval": 10 },
    { "distance": 287, "interval": 56 },
    { "distance": 346, "interval": 93 },
    { "distance": 173, "interval": 25 },
    { "distance": 898, "interval": 82 },
    { "distance": 251, "interval": 19 },
    { "distance": 8691, "interval": 423 },
    { "distance": 26219, "interval": 1539 },
    { "distance": 18633, "interval": 1003 },
    { "distance": 44, "interval": 5 },
    { "distance": 1141, "interval": 121 },
    { "distance": 27601, "interval": 1948 },
    { "distance": 1484, "interval": 232 },
    { "lon": 99.978337, "lat": 14.022788, "title": "จุดปลายทาง", "distance": 85997, "interval": 5616 }
]


 