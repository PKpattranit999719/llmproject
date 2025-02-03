from turtle import st
import streamlit as st
import requests
import urllib.parse
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
import folium
from geopy.distance import geodesic
from IPython.display import display
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

        # print(f"Raw extracted event: {event}")  # เช็คค่าที่ได้จาก chain.invoke
        
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
        response.raise_for_status()
        route_data = response.json()
        print(route_data)
    
        print(f"Route data received: {route_data}")  # เช็คค่าที่ได้จาก API
    
        return route_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching route data: {e}")
    return None

def get_lat_lon_from_osm(searched_location):
    """
    Get latitude and longitude from OpenStreetMap Nominatim API.

    Args:
        searched_location (str): The name of the place to search.

    Returns:
        tuple: Latitude and longitude of the searched place, or None if not found.
    """
    url = f'https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(searched_location)}&format=json'
    headers = {'User-Agent': 'MyGeocodingApp/1.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # จะตรวจสอบว่า HTTP request สำเร็จหรือไม่
        data = response.json()
        
        if data:
            lat = data[0].get('lat')
            lon = data[0].get('lon')
            return lat, lon
    except requests.exceptions.RequestException as e:
        print(f"Error during geocoding: {e}")
    
    return None, None

def get_places_from_route(route_data):
    """
    Extract place name, latitude, and longitude from route data using OpenStreetMap Nominatim API.
    
    Args:
        route_data (dict): Route data containing the list of guide points.

    Returns:
        list: A list of dictionaries containing place_name, latitude, and longitude.
    """
    places_with_coordinates = []

    # ตรวจสอบว่า route_data มีข้อมูลและ 'data' มีค่าว่างหรือไม่
    if 'data' in route_data and isinstance(route_data['data'], list) and len(route_data['data']) > 0:
        # ใช้ .get() เพื่อดึงข้อมูล guide จาก data[0] โดยไม่ให้เกิดข้อผิดพลาด
        guide_points = route_data['data'][0].get('guide', [])
        
        for point in guide_points:
            name = point.get('name')
            
            print(f"Processing point: {name}")  # ดูว่าได้ค่าจุดไหนมาบ้าง
            
            if name:
                latitude, longitude = get_lat_lon_from_osm(name)
                
                print(f"Resolved coordinates for {name}: lat={latitude}, lon={longitude}")  # ตรวจสอบค่าที่ได้จาก OSM API
                
                if latitude and longitude:
                    places_with_coordinates.append({
                        "place_name": name,
                        "latitude": latitude,
                        "longitude": longitude
                    })
    else:
        print("Route data is empty or has an invalid structure.")
    
    return places_with_coordinates


def search_interest_logdo_map_api(keyword, location, radius):
    try:
        base_url = "https://search.longdo.com/mapsearch/json/search?" 
        params = {
            'key': '7b6f8a4c53a57fa8315fbdcf5b108c83',
            'lon': location[1],
            'lat': location[0],
            'radius': radius * 1000,
            'keyword': keyword
        }
        full_url = base_url + urllib.parse.urlencode(params)

        response = requests.get(full_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Longdo API: {e}")
    return None

def search_places_of_interest(flon, flat, tlon, tlat, keyword, radius):
    """
    Get route data and search for places of interest along the route.

    Args:
        flon (float): Longitude of the start point.
        flat (float): Latitude of the start point.
        tlon (float): Longitude of the destination point.
        tlat (float): Latitude of the destination point.
        keyword (str): Keyword to search for places of interest.
        radius (int): Radius in kilometers to search for places around each point.

    Returns:
        list: A list containing places of interest along the route.
    """
    route_data = get_route_data(flon, flat, tlon, tlat)
    
    # print(f"Fetched route data: {route_data}")  # ตรวจสอบข้อมูลที่ได้จาก API
    
    if not route_data:
        print("Failed to fetch route data.")
        return []
    
    # Extract coordinates from route_data
    places_with_coordinates = get_places_from_route(route_data)
    
    # Search for places of interest using the extracted coordinates
    places_of_interest = []
       
    for place in places_with_coordinates[:5]:
        latitude = place["latitude"]
        longitude = place["longitude"]
        
        found_places = search_interest_logdo_map_api(keyword, (latitude, longitude), radius)
     
        # print(f"📍 Found places at ({latitude}, {longitude}):", found_places)  # Debug
        places_of_interest.append(found_places)
    
    return places_of_interest

################################ ค่าในฟังชั่นด้านบนก็มีค่าหมดนะได้ทำการ print เช็คค่าแล้ว #########################################33
# ใช้ในการเรียงตำแหน่งของเส้นทาง เราจะไปเรียกใช่ใน main  เดี๋ยวต้องไปทำการเขียนการเรียกใช้ใหม่ เดี๋ยวจะลบออก
def sort_points(points, user_location, user_destination):
    """
    Sort points based on distance from the starting point sequentially.

    Args:
        points (list): List of dictionaries containing place_name, latitude, and longitude.
        start (dict or tuple or list): Start point, can be a dict, tuple, or list.
        end (dict or tuple or list): End point, can be a dict, tuple, or list.

    Returns:
        list: List of sorted points (excluding start but including end).
    """

    # # ฟังก์ชันแปลงข้อมูลเป็น dictionary
    # def convert_to_dict(point):
    #     if isinstance(point, dict):
    #         return point  # ถ้าเป็น dictionary แล้วไม่ต้องแปลง
    #     elif isinstance(point, (tuple, list)) and len(point) == 3:
    #         return {"place_name": point[0], "latitude": point[1], "longitude": point[2]}
    #     else:
    #         raise ValueError("Point must be a tuple, list, or dictionary with three elements.")

    # # แปลง start และ end ถ้าไม่ใช่ dictionary
    # start = convert_to_dict(start)
    # end = convert_to_dict(end)

    # # ตรวจสอบว่า points ทุกตัวใน list เป็น dictionary
    # if not all(isinstance(p, dict) for p in points):
    #     raise ValueError("All points must be dictionaries.")

    # # ตรวจสอบว่าแต่ละ dictionary ใน points, start, และ end มี key ที่ต้องการ
    # required_keys = ['place_name', 'latitude', 'longitude']
    # for point in [start, end] + points:
    #     if not all(key in point for key in required_keys):  # ตรวจสอบว่าแต่ละ dictionary มี key ที่ต้องการหรือไม่
    #         raise ValueError(f"Each point must contain keys: {required_keys}")

    sorted_points = [user_location]  # เริ่มต้นที่จุดเริ่มต้น
    points = points.copy()  # สร้างสำเนาของ list points
    current_point = user_location  # เริ่มจากจุดเริ่มต้น

    # เรียงลำดับจุดตามระยะทางจากจุดเริ่มต้น
    while points:
        next_point = min(points, key=lambda p: geodesic(
            (current_point["latitude"], current_point["longitude"]),
            (p["latitude"], p["longitude"])
        ).meters)
        
        sorted_points.append(next_point)
        points.remove(next_point)
        current_point = next_point  # อัปเดตจุดปัจจุบัน

    sorted_points.append(user_destination)  # เพิ่มจุดปลายทางเข้าไปตอนจบ
    # print(f"****Sorted points: {[p['place_name'] for p in sorted_points]}")  # Debugging
    return sorted_points[1:]  # ตัดจุดเริ่มต้นออกจากผลลัพธ์


# เรื่องทำการแสดงแผนที่ แบ่งเป็นการแสดงเส้นทาง และ การแสดงสถานที่ที่น่าสนใจ
def create_map(route_data, places_of_interest, start_location, end_location, places_with_coordinates):
    """
    Create and display a map with route data and places of interest.

    Args:
        route_data (dict): Route information containing guide points.
        places_of_interest (list): List of places containing additional information.
        start_location (tuple): Starting point (lat, lon).
        end_location (tuple): Ending point (lat, lon).
        places_with_coordinates (list): List of places with coordinates.
    """
    if not route_data:
        print("No route data available.")
        return

    # Create the base map centered between start and end locations
    midpoint = (
        (start_location[0] + end_location[0]) / 2,
        (start_location[1] + end_location[1]) / 2
    )
    m = folium.Map(location=midpoint, zoom_start=12)

    # Add markers for start and end locations
    folium.Marker(
        location=start_location,
        popup="Start Location",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    folium.Marker(
        location=end_location,
        popup="End Location",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    # Add markers for the places in places_with_coordinates
    if places_with_coordinates:
        for idx, point in enumerate(places_with_coordinates):
            folium.Marker(
                location=[point["latitude"], point["longitude"]],
                popup=f"{idx + 1}: {point['place_name']}",
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)

        # Draw the route line connecting the points (from start to places and to the end)
        route_coords = [[point["latitude"], point["longitude"]] for point in places_with_coordinates]
        folium.PolyLine([start_location] + route_coords + [end_location], color="blue", weight=3, opacity=0.8).add_to(m)

    # Extract places of interest and add them to the map
    places_data = extract_and_return_data_from_places(places_of_interest)

    for data in places_data:
        place_name = data.get('place_name', '')
        place_lat = data.get('place_lat', '')  # Use 'place_lat' as it is stored in extracted data
        place_lon = data.get('place_lon', '')  # Use 'place_lon' as it is stored in extracted data

        # print(f"Adding place: {place_name}, Lat: {place_lat}, Lon: {place_lon}")  # Debugging

        # Check if latitude and longitude are valid before adding marker
        try:
            place_lat = float(place_lat)
            place_lon = float(place_lon)
            folium.Marker(
                location=[place_lat, place_lon],
                popup=f"Place: {place_name}",
                icon=folium.Icon(color='purple', icon='info-sign')
            ).add_to(m)
        except ValueError:
            print(f"Skipping place {place_name} due to invalid coordinates.")

    map_html = m._repr_html_()  # Get the HTML representation of the map
    st.components.v1.html(map_html, height=600)  # Display the map in Streamlit
            # Display the map
    # display(m)

# เนื่องจากรูปแบบของข้อมูลใน ฟังขั่น search_places_of_interest ไม่ตรงกับรูปแบบในการวิเคราะห์แผนที่เลยต้องมาปรับรูปแบบกันก่อน
def extract_and_return_data_from_places(places_of_interest):
    """
    Extract and return data from places_of_interest.
    Args:
        places_of_interest (list): List of places containing place_name and data.
    Returns:
        list: A list of dictionaries containing the name, latitude, and longitude of places.
    """
    extracted_data = []
 
    print("--------------------------------------------------------------------------------------")
    for place in places_of_interest:  # วนลูปใน places_of_interest
        data_list = place.get("data", [])  # ดึงค่า data ออกมา (เป็น list)
        
        for val in data_list:  # วนลูปใน data เพื่อดึงค่า lat/lon
            place_name = val.get("name", "Unknown")
            place_lat = val.get("lat", "Unknown")
            place_lon = val.get("lon", "Unknown")
            
            extracted_data.append({
                'place_name': place_name,
                'place_lat': place_lat,
                'place_lon': place_lon,
            })

    # print(extracted_data)  # ตรวจสอบผลลัพธ์
    print("--------------------------------------------------------------------------------------")
        # ตรวจสอบข้อมูลย่อยที่อาจจะมี
        # places_data = place.get('places', {}).get('data', [])
        # if places_data:
        #     for data in places_data:
        #         data_name = data.get('name', 'Unknown')
        #         data_lat = data.get('lat', 'Unknown')
        #         data_lon = data.get('lon', 'Unknown')

        #         # เก็บข้อมูลสถานที่ที่ดึงมา
        #         extracted_data.append({
        #             'place_name': place_name,
        #             'place_lat': place_lat,
        #             'place_lon': place_lon,
        #             'name': data_name,
        #             'lat': data_lat,
        #             'lon': data_lon
        #         })
        # else:
        #     # ถ้าไม่มีข้อมูลย่อยก็เพิ่มสถานที่หลัก
        #     extracted_data.append({
        #         'place_name': place_name,
        #         'place_lat': place_lat,
        #         'place_lon': place_lon
        #     })

    return extracted_data

# ทำการวิเคราะห์สถานที่  ข้อมูลไม่เข้าฟังชั่นนี้
# def extract_and_analyze_data(places_of_interest):
#     """
#     Extract and analyze data from places_of_interest, considering factors like convenience, opening hours, price, and reviews.
#     Args:
#         places_of_interest (list): List of places containing place_name and data.
#     Returns:
#         list: A list of dictionaries containing place analysis including convenience, price, and reviews.
#     """
#     analyzed_data = []

#     if not places_of_interest:
#         print("No places of interest to analyze.")
#         return analyzed_data

#     for place in places_of_interest:
#         place_name = place.get('name', 'Unknown')
#         place_lat = place.get('lat', 'Unknown')
#         place_lon = place.get('lon', 'Unknown')

#         places_data = place.get('places', {}).get('data', [])
#         if places_data:
#             for data in places_data:
#                 data_name = data.get('name', 'Unknown')
#                 data_lat = data.get('lat', 'Unknown')
#                 data_lon = data.get('lon', 'Unknown')
#                 opening_hours = data.get('opening_hours', 'Unknown')
#                 price_range = data.get('price_range', 'Unknown')
#                 reviews = data.get('reviews', [])

#                 # คำนวณคะแนนจากรีวิว
#                 average_review_score = 0
#                 if reviews:
#                     total_score = sum(review.get('score', 0) for review in reviews)
#                     average_review_score = total_score / len(reviews)

#                 # คำนวณระยะทางเพื่อให้คะแนนความสะดวก
#                 distance = calculate_distance(place_lat, place_lon, data_lat, data_lon)
#                 convenience_score = max(0, 10 - distance)

#                 analyzed_data.append({
#                     'place_name': place_name,
#                     'place_lat': place_lat,
#                     'place_lon': place_lon,
#                     'name': data_name,
#                     'lat': data_lat,
#                     'lon': data_lon,
#                     'opening_hours': opening_hours,
#                     'price_range': price_range,
#                     'average_review_score': average_review_score,
#                     'convenience_score': convenience_score
#                 })
#         else:
#             # ถ้าไม่มีข้อมูลย่อย ก็เก็บเฉพาะข้อมูลสถานที่หลัก
#             analyzed_data.append({
#                 'place_name': place_name,
#                 'place_lat': place_lat,
#                 'place_lon': place_lon
#             })

#     print(analyzed_data)
    
#     return analyzed_data

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two coordinates (in kilometers).
    Args:
        lat1, lon1 (float): Coordinates of the starting point.
        lat2, lon2 (float): Coordinates of the destination point.
    Returns:
        float: The distance between the two points in kilometers.
    """
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

def recommend_places(places_of_interest, keyword, radius):
    """
    Use LLM to recommend places based on analyzed data.

    Args:
        places_of_interest: The places for after searching.
        keyword (str): The keyword used for searching.
        radius (int): Radius in kilometers to search for places around each point.

    Returns:
        str: LLM response with recommendations.
    """
    if not places_of_interest:
        return "ไม่มีสถานที่ที่พบตามคำค้นหา."
    
    # Generate the information string for LLM prompt
    places_info = "\n".join([f"{index+1}. {place.get['name']} (ระยะห่าง: {place.get('distance', 'N/A'):.2f} กม.) - [ดูเพิ่มเติม](https://www.wongnai.com/search?query={place['name']})" for index, place in enumerate(places_of_interest)])

    prompt = f"""
    คำค้นหาของผู้ใช้: "{keyword}"
    ต่อไปนี้คือสถานที่ที่พบจากคำค้นหา:
    {places_info}

    กรุณาแนะนำสถานที่ที่ดีที่สุดจากรายการนี้ โดยพิจารณาจากความน่าสนใจ, ความสะดวกในการเข้าถึง, และประเภทของสถานที่, ลักษณะการเดินทาง มีที่จอดรถหรือป่าว, รสชาติอาหารอร่อยหรือป่าว, เหมาะกับเด็กหรือผู้สูงอายุมั้ย.
    โปรดให้ข้อมูลเพิ่มเติมว่าแนะนำจากการวิเคราะห์ใด.
    """

    try:
        # Send the prompt to LLM for recommendation
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"Error generating recommendation: {e}")
        return "เกิดข้อผิดพลาดในการให้คำแนะนำ."

   
def explain_route_with_llm(route_data):
    # ตรวจสอบว่าข้อมูลไม่เป็น None และมีโครงสร้างที่ถูกต้อง
    if not route_data or 'data' not in route_data or not route_data['data']:
        return "❌ ไม่มีข้อมูลเส้นทาง"

    first_route = route_data['data'][0]
    if 'guide' not in first_route or not first_route['guide']:
        return "❌ ไม่มีคำแนะนำเส้นทาง"

    route_steps = []
    for instruction in first_route['guide']:
        turn = instruction.get('turn', 'ไม่ระบุ')
        name = instruction.get('name', 'ไม่ระบุ')
        distance = instruction.get('distance', 'ไม่ระบุ')
        interval = instruction.get('interval', 'ไม่ระบุ')
        step = f"🔹 เลี้ยวที่ {turn} ไปที่ {name}, ระยะทาง {distance} เมตร, ระยะห่าง {interval} เมตร"
        route_steps.append(step)

    route_description = "\n".join(route_steps)

    # print(f"✅ Route description generated:\n{route_description}")  # ตรวจสอบก่อนส่งให้ LLM

    prompt = f"""
    นี่คือคำแนะนำการเดินทาง:
    {route_description}

    กรุณาอธิบายเส้นทางให้อ่านง่ายสำหรับคนที่ไม่เคยไปมาก่อน
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
  

# #### ต้องเขียนลำดับการเรียกการทำงาน ใน main ในส่วนนี้ ######
# ตัวอย่างข้อมูลจากการเรียกใช้ API
# places_interest = "อยากกินข้าว"
# user_location = (13.7563, 100.5018)  # จุดเริ่มต้น กรุงเทพฯ
# user_destination = (14.022788, 99.978337)  # จุดสิ้นสุด กาญจนบุรี
# radius = 5  # รัศมีการค้นหาสถานที่ 5 กิโลเมตร

# keyword = process_places_of_interest_routes(places_interest)  # ฟังก์ชันที่ใช้ในการแยก keyword จาก query
# if keyword:
#     print(f"Extracted Keyword: {keyword}")

#     route_points = [
#             (float(places_of_interest['latitude']), float(places_of_interest['longitude']))
#             for route in search_places_of_interest
#         ]

#         # Sort the points based on their proximity to each other starting from the user's location
#     sorted_route_points = sort_points(route_points, user_location)


# # เรียกใช้ฟังก์ชันเพื่อดึงข้อมูลเส้นทางและสถานที่น่าสนใจ
# flon, flat, tlon, tlat = convert_locations(user_location, user_destination)  # ฟังก์ชันที่ใช้แปลงค่าพิกัด

# print("\n--- Searching places along the route ---")
# route_data, places_of_interest = get_places_from_route(flon, flat, tlon, tlat, keyword, radius)
# if places_of_interest:
#     analyzed_places = extract_and_analyze_data(places_of_interest)
# else:
#     print("No places of interest found.")
# # สร้างแผนที่
# create_map(route_data, places_of_interest, user_location, user_destination, sorted_route_points)


# print("\n--- LLM Recommendations ---")
# recommendations = recommend_places(places_of_interest, keyword, top_n=10)
# print(recommendations)

# explanation = explain_route_with_llm(route_data)  
# # แสดงคำอธิบายการเดินทาง
# display_route_explanation(explanation)
