import math
import time
import streamlit as st
import requests
import urllib.parse
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
import streamlit.components.v1 as components 


# Define a model for keyword extraction
class SearchKeyword(BaseModel):
    keyword: str

# Initialize LLM with centralized server configuration
url = 'http://111.223.37.52/v1'
api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7Im9yZ2FuaXphdGlvbl9pZCI6IjY3NjhkNzA3YjNiYmM5MWQwYWNjMWNjNCIsInRva2VuX25hbWUiOiJCYW5rIiwic3RkRGF0ZSI6IjIwMjUtMDEtMTlUMTc6MDA6MDAuMDAwWiJ9LCJpYXQiOjE3MzczNTkxMDcsImV4cCI6MTc0MDU4OTE5OX0.7peNsGJSnQL2tctiui3MXTBc5OZsLv8OSizh68KVH5w'

llm = ChatOpenAI(
    model="gpt-4o-mini",
    base_url=url,
    api_key=api_key,
    max_tokens=1000
)

def clean_keyword(keyword: str):
    return keyword.strip().lower()

def process_places_of_interest_routes(places_interest):
    try:
        parser = JsonOutputParser(pydantic_object=SearchKeyword)
        format_instructions = """
        คุณต้องกรองคำสำคัญจากคำขอของผู้ใช้.
        คำขอของผู้ใช้คือ: {places_of_interest}
        คำสำคัญที่คุณต้องการหาคือสิ่งที่เกี่ยวข้องกับการค้นหาหรือการกระทำที่ผู้ใช้ต้องการ เช่น:
        - ต้องการทานข้าวหรือแวะพักทานอาหาร: "ร้านอาหาร"
        - ต้องการทานกาแฟ: "ร้านกาแฟ"
        - หากผู้ใช้ต้องการหาห้องน้ำ: "ห้องน้ำ"
        - หากผู้ใช้ต้องการเติมน้ำมัน: "ปั๊มน้ำมัน"
        - หากผู้ใช้ต้องการซื้อของฝาก: "ร้านขายของฝาก"
        - หากผู้ใช้ต้องการซื้อของ: "ร้านสะดวกซื้อ"
        - หากผู้ใช้ต้องการสถานที่แวะพักระหว่างการเดินทาง: "สถานที่พัก"
        กรุณาตอบคำสำคัญที่พบในคำขอนี้ในรูปแบบ JSON ตามตัวอย่างนี้:
        {
            "keyword": "<extracted_keyword>"
        }
        """
        
        prompt = PromptTemplate(
            template="""\
            ## คุณมีหน้าที่กรองคำสำคัญจากคำขอผู้ใช้.

            # คำขอผู้ใช้: {places_of_interest}

            # Your response should be structured as follows:
            {format_instructions}
            """,
            input_variables=["places_of_interest"],
            partial_variables={"format_instructions": format_instructions},
        )

        chain = prompt | llm | parser
        event = chain.invoke({"places_of_interest": places_interest})

        print(f"Raw extracted event: {event}")  # เช็คค่าที่ได้จาก chain.invoke
        
        if event:
            keyword = event.get('keyword', '')
            cleaned_keyword = clean_keyword(keyword)
            if cleaned_keyword:
                return cleaned_keyword
    except Exception as e:
        print(f"Error processing user query: {e}")
        return None
    
def convert_locations(user_location, user_destination):
    flat, flon = user_location
    tlat, tlon = user_destination
    return flon, flat, tlon, tlat

def get_route_data(flon, flat, tlon, tlat):
    """
    Get the route data from the Longdo API based on the given start and end points.

    Args:
        flon (float): Longitude of the start point.
        flat (float): Latitude of the start point.
        tlon (float): Longitude of the destination point.
        tlat (float): Latitude of the destination point.

    Returns:
        dict: Route data returned by the Longdo API.
    """
    try:
        base_url = "https://api.longdo.com/RouteService/json/route/guide?"
        params = {
            'key': '7b6f8a4c53a57fa8315fbdcf5b108c83',
            'flon': flon,
            'flat': flat,
            'tlon': tlon,
            'tlat': tlat
        }
        full_url = base_url + urllib.parse.urlencode(params)

        response = requests.get(full_url)
        route_data = response.json()
        return route_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching route data: {e}")
    return None

# เราจะเอาค่าของ get_route_data มาทำการวนลูปหาเส้นทาง
def get_route_path_from_id(id):
    route_path_list = []
    try:
        
        print("id",id)
        base_url = f"https://api.longdo.com/RouteService/json/route/path?id={id}"

        response = requests.get(base_url)
   
        route_path_data = response.json()

        # # แสดงข้อมูลเส้นทางที่ได้
        # print("Route Path Data:", route_path_data)

        # # เก็บข้อมูลเส้นทางใน route_path_list
        # if route_path_data:
        #     route_path_list.append(route_path_data)
        #print(route_path_list)
        return route_path_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching route path data: {e}")
    return route_path_list

def search_interest_logdo_map_api(keyword, location, radius):
    try:
        base_url = "https://search.longdo.com/mapsearch/json/search"
        params = {
            'key': '7b6f8a4c53a57fa8315fbdcf5b108c83',
            'lon': location[1],
            'lat': location[0],
            'span': radius,
            'keyword': keyword
    }

        response = requests.get(base_url, params=params)
        time.sleep(0.5)  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Longdo API: {e}")
    return None

def search_places_of_interest(route_path_list, keyword, radius):    
    places_of_interest=[]
    for add in route_path_list['data']:
        middle_index = math.floor(len(add) / 2) 
        # LLm เช็ค
        selected_places = [add[0], add[middle_index], add[-1]]        
        for place in selected_places:
            latitude = place["lat"]
            longitude = place["lon"]
            found_places = search_interest_logdo_map_api(keyword, (latitude, longitude), radius)
            ddot = extract_and_return_data_from_places(found_places)

            places_of_interest.extend(ddot)
    return places_of_interest

# แผนที่ที่ใช้โดย Longdo map
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
                    map.Route.search() 
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

def extract_and_return_data_from_places(places_of_interest):
    extracted_data = []

    if isinstance(places_of_interest, dict):
        data_list = places_of_interest.get("data", [])
        
        if data_list: 
            selected_places = [data_list[0], data_list[-1]]
            for val in selected_places:
                place_name = val.get("name", "")
                place_lat = val.get("lat", "")
                place_lon = val.get("lon", "")
                extracted_data.append({
                    'place_name': place_name,
                    'place_lat': place_lat,
                    'place_lon': place_lon,
                    
                })
 
    return extracted_data
def recommend_places(places_with_coordinates, places_of_interest, keyword):
    """
    ใช้ LLM วิเคราะห์และแนะนำสถานที่ โดยไม่ต้องคำนวณระยะทาง

    Args:
        places_with_coordinates (list): เก็บชื่อสถานที่และละติจูด และ ลองจิจูดเป็นจุดในเส้นทาง
        places_of_interest (list): สถานที่ที่พบ
        keyword (str): คำค้นหา

    Returns:
        str: คำแนะนำจาก LLM
    """
    # จัดรูปแบบข้อมูลส่งให้ LLM โดยส่งข้อมูลทั้งหมดของ places_of_interest
    places_info = "\n".join([f"{index+1}. {place.get('name', 'Unknown')} (Lat: {place.get('lat', 'N/A')}, Lon: {place.get('lon', 'N/A')})"
                            for index, place in enumerate(places_of_interest)])
    prompt = f"""
    คำค้นหาของผู้ใช้: "{keyword}"
    
    ต่อไปนี้คือสถานที่ที่พบในบริเวณรอบๆ เส้นทางที่คุณกำลังเดินทาง:
    {places_info}

    กรุณาแนะนำ 5 สถานที่ที่ดีที่สุดจากรายการนี้ โดยพิจารณาจาก:
    - ความสะดวกในการเข้าถึง
    - ประเภทของสถานที่ (ร้านอาหาร, คาเฟ่, จุดท่องเที่ยว ฯลฯ)
    - ลักษณะการเดินทาง (เดิน, ขับรถ, มีที่จอดรถ)
    - ความนิยมของสถานที่
    - ความเหมาะสมสำหรับเด็กหรือผู้สูงอายุ

    โปรดอธิบายเหตุผลว่าทำไมคุณถึงเลือกสถานที่แนะนำ.
    """

    try:
        # ส่งคำขอไปยัง LLM
        response = llm.invoke(prompt)

        # ตรวจสอบว่ามีค่า response หรือไม่
        if not response:
            print("No response received from LLM.")
        
        # ตรวจสอบว่า response มีเนื้อหาหรือไม่
        if response and hasattr(response, 'content'):
            print("LLM Response:", response.content)  # แสดงค่าใน console
            return response.content.strip()  # คืนค่าเนื้อหา
        else:
            print("No content found in response.")
            return "ไม่สามารถให้คำแนะนำได้."
    
    except Exception as e:
        # จับข้อผิดพลาดที่เกิดขึ้นจากการเรียกใช้ LLM
        print(f"Error generating recommendation: {e}")
        return "เกิดข้อผิดพลาดในการให้คำแนะนำ."

def explain_route_with_llm(route_data):
    # ตรวจสอบว่าข้อมูลไม่เป็น None และมีโครงสร้างที่ถูกต้อง
    if not route_data or 'data' not in route_data or not route_data['data']:
        return "❌ ไม่มีข้อมูลเส้นทาง"

    first_route = route_data['data'][0]
    if 'guide' not in first_route or not first_route['guide']:
        return "❌ ไม่มีคำแนะนำเส้นทาง"

    # 🔹 แปลง TurnCode เป็นข้อความที่เข้าใจง่าย
    turn_code_mapping = {
        0: "เลี้ยวซ้าย",
        1: "เลี้ยวขวา",
        2: "เลี้ยวซ้ายเล็กน้อย",
        3: "เลี้ยวขวาเล็กน้อย",
        4: "ทิศทางไม่ระบุ",
        5: "ตรงไป",
        6: "เข้าสู่ทางด่วน",
        9: "ถึงที่หมาย",
        11: "เดินทางโดยเรือเฟอร์รี่"
    }

    route_steps = []
    total_distance = 0  # ระยะทางรวม
    total_time = 0       # เวลารวม

    for instruction in first_route['guide']:
        turn_code = instruction.get('turn', 4)  # ค่าเริ่มต้นคือ "ทิศทางไม่ระบุ"
        turn = turn_code_mapping.get(turn_code, "ไม่ระบุทิศทาง")
        name = instruction.get('name', 'ไม่ระบุ')
        distance = instruction.get('distance', 0)  # ระยะทาง (เมตร)
        interval = instruction.get('interval', 0)  # เวลา (วินาที)

        total_distance += distance
        total_time += interval

        step = f"🔹 {turn} ไปที่ {name}, ระยะทาง {distance} เมตร, ใช้เวลา {interval} วินาที"
        route_steps.append(step)

    # แปลงหน่วยของระยะทางและเวลา
    total_distance_km = total_distance / 1000  # แปลงเมตรเป็นกิโลเมตร
    total_time_min = total_time / 60  # แปลงวินาทีเป็นนาที

    route_description = "\n".join(route_steps)

    print(f"✅ Route description generated:\n{route_description}")  # Debug

    # 🔹 สร้าง Prompt ให้ LLM
    prompt = f"""
        นี่คือคำแนะนำการเดินทาง:

        {route_description}

        ข้อมูลเสริม:
        - ระยะทางรวม: {total_distance_km:.2f} กิโลเมตร
        - เวลาทั้งหมด: {total_time_min:.1f} นาที

        กรุณาอธิบายเส้นทางให้อ่านง่ายสำหรับคนที่ไม่เคยไปมาก่อน โดยให้ข้อมูลการเดินทางในรูปแบบดังนี้:

        1. เริ่มต้นที่ [ชื่อจุดเริ่มต้น]
        2. เดินทางไปที่ [ชื่อถนนหรือสถานที่]
            - ระยะทาง: [ระยะทางเป็นเมตร] เมตร (ใช้เวลา [เวลาเป็นวินาที/นาที])
        3. [รายละเอียดเพิ่มเติมเกี่ยวกับจุดถัดไป]
            - ระยะทาง: [ระยะทาง] เมตร (ใช้เวลา [เวลา])
        4. ต่อไปในลักษณะเดียวกันสำหรับทุกจุด

        สรุปรวมทั้งหมด:
        - ระยะทางทั้งหมดที่เดินทาง จากจุดเริ่มต้นมายังจุดหมายปลายทาง คือ [รวมระยะทางทั้งหมด] เมตร/กิโลเมตร (แปลงจากเมตรเป็นกิโลเมตรถ้ามากกว่า 1000 เมตร)
        - เวลาที่ใช้ในการเดินทางทั้งหมดคือ [รวมเวลา] นาที (ถ้ามากกว่า 60 นาที ให้แสดงเป็นชั่วโมง เช่น 1 ชม. 30 นาที)
        """
    try:
        if hasattr(llm, 'invoke'):
            response = llm.invoke(prompt)
            return response.content.strip()
        else:
            return "❌ LLM ไม่พร้อมใช้งาน"
    except Exception as e:
        print(f"❌ Error generating description: {e}")
        return "❌ เกิดข้อผิดพลาดในการอธิบายเส้นทาง"

# ฟังก์ชันการแสดงคำอธิบายการเดินทาง
def display_route_explanation(route_data):
    explanation = explain_route_with_llm(route_data)
    print("📌 คำอธิบายเส้นทางจาก LLM:", explanation)
