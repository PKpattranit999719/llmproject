import math
import re
import time
from typing import List
import requests
import urllib.parse
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import streamlit.components.v1 as components 
from datetime import datetime
import pytz 

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
)

def clean_keyword(keyword: str):
    return keyword.strip().lower()

def process_places_of_interest_routes(places_interest):
    try:
        parser = JsonOutputParser(pydantic_object=SearchKeyword)
 
        prompt = PromptTemplate(
            template="""\
            ## คุณมีหน้าที่กรองคำสำคัญจากคำขอผู้ใช้.

            # คำขอผู้ใช้: {places_of_interest}
            คำสำคัญที่คุณต้องการหาคือสิ่งที่เกี่ยวข้องกับการค้นหาหรือการกระทำที่ผู้ใช้ต้องการ เช่น:
                - ต้องการทานข้าวหรือแวะพักทานอาหาร: "ร้านอาหาร"
                - ต้องการทานกาแฟ: "ร้านกาแฟ"
                - หากผู้ใช้ต้องการหาห้องน้ำ: "ห้องน้ำ"
                - หากผู้ใช้ต้องการเติมน้ำมัน: "ปั๊มน้ำมัน"
                - หากผู้ใช้ต้องการซื้อของฝาก: "ร้านขายของฝาก"
                - หากผู้ใช้ต้องการซื้อของ: "ร้านสะดวกซื้อ"
                - หากผู้ใช้ต้องการสถานที่แวะพักระหว่างการเดินทาง: "สถานที่พัก"
            # Your response should be structured as follows:
            {format_instructions}
            """,
            input_variables=["places_of_interest"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
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

def get_route_path_from_id(id):
    route_path_list = []
    try:
       
        base_url = f"https://api.longdo.com/RouteService/json/route/path?id={id}"
        response = requests.get(base_url)
        route_path_data = response.json()
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
            'span': '150m',
            'keyword': keyword
    }

        response = requests.get(base_url, params=params)
        print(response)
        time.sleep(0.3)  

        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Longdo API: {e}")
    return None

def search_places_of_interest(route_path_list, keyword, radius, places_interest):    
    places_of_interest=[]
    for add in route_path_list['data']:
         # LLm เช็ค
        # selected_places = [add[0], add[middle_index], add[-1]]              
        selected_places = [add[i] for i in range(0, len(add), 15)]
   
    
        for place in selected_places:
            latitude = place["lat"]
            longitude = place["lon"]
            found_places = search_interest_logdo_map_api(keyword, (latitude, longitude), radius)
            ddot = extract_and_return_data_from_places(found_places)

            places_of_interest.extend(ddot)

    rec = []
    seen = set()
    check_point = [] 
    rec = []   

    for place in places_of_interest:
        key = (place["lon"], place["lat"], place["name"])
        
        if key not in seen:
            seen.add(key) 
            check_point.append({
                "lon": place["lon"],
                "lat": place["lat"],
                "title": place["name"]
            })
            
            rec.append({
                "name": place["name"], 
                "working_hours": place.get("working_hours", None),
                "tag": place.get("tag", None),
                "url": place.get("url", None),
                "address": place.get("address", None),
                "tel": place.get("tel", None),
                "url" :place.get("tel", None),
            })
 
    class ModelGuide(BaseModel):
        name: str = Field(description="ชื่อสถานที่")
        recommend: str = Field(description="แนะนำเพราะอะไร ขอรายละเอียดเยอะในระดับหนึ่ง รายละเอียดที่อยากได้ เวลาตอนนี้อยู่ในช่วงเวลาทำการ หรืออาจแนะนำว่า เพราะสถานที่ตรงร้านน่าสนใจ หรืออื่นๆให้สอดคล้องกับข้อความจากผู้ใช้")

    class Guide(BaseModel):
        guide: List[ModelGuide] = Field(description="ลิสต์ของสถานที่ที่แนะนำ")
            
    parser = JsonOutputParser(pydantic_object=Guide)
 
    prompt = PromptTemplate(
            template="""\
            ## ตอนนี้คุณเป็นเหมือนไกด์ ที่จะแนะนำ สถานที่ตามข้อความจาก ผู้ใช้ และข้อมูลสถานที่ที่มี โดย แนะนำไม่เกิน 5 สถานที่. หากร้านไหนมีระบุเวลาเปิดปิด ตรงกับเวลาตอนนี้จะแนะนำเป็นพิเศษ
            # เวลาตอนนี้ : {date}

            # ข้อความจาก ผู้ใช้: {places_interest}
            
            ## ข้อมูลสถานที่ : 
            {data}

            # Your response should be structured as follows:
            {format_instructions}
            """,
            input_variables=["data", "places_interest", "date"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
    
    thailand_tz = pytz.timezone('Asia/Bangkok')

    now = datetime.now(thailand_tz)

    day_of_week = now.strftime('%A') 
    # day_of_week_thai = {
    #     "Monday": "จันทร์", "Tuesday": "อังคาร", "Wednesday": "พุธ", "Thursday": "พฤหัส", 
    #     "Friday": "ศุกร์", "Saturday": "เสาร์", "Sunday": "อาทิตย์"
    # }.get(day_of_week, day_of_week)
    time_str = now.strftime('%H:%M')
 
    chain = prompt | llm | parser
    event = chain.invoke({"data": rec, "places_interest": places_interest, "date": f"{day_of_week} timenow: {time_str}" })
    print(event["guide"])
    return event["guide"], check_point

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
            for val in data_list:
                extracted_data.append(val)
 
    return extracted_data

def recommend_places(places_of_interest, keyword):
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
