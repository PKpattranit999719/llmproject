import requests
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import folium
import ipywidgets as widgets
from IPython.display import display
import streamlit as st
from streamlit.components.v1 import html
from langchain_core.tools import StructuredTool
#from function_routes import convert_locations, get_places_from_route, process_places_of_interest_routes, sort_points, create_map

# กำหนดค่า API และ URL สำหรับการเชื่อมต่อ LLM
url = 'http://111.223.37.52/v1'
api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7Im9yZ2FuaXphdGlvbl9pZCI6IjY3NjhkNzA3YjNiYmM5MWQwYWNjMWNjNCIsInRva2VuX25hbWUiOiJCYW5rIiwic3RkRGF0ZSI6IjIwMjUtMDEtMTlUMTc6MDA6MDAuMDAwWiJ9LCJpYXQiOjE3MzczNTkxMDcsImV4cCI6MTc0MDU4OTE5OX0.7peNsGJSnQL2tctiui3MXTBc5OZsLv8OSizh68KVH5w'

llm = ChatOpenAI(
    model='gpt-4o-mini',
    base_url=url,  
    api_key=api_key,  
    max_tokens=1000  
)

# สร้างโมเดล Pydantic สำหรับการจัดการข้อมูลคำสำคัญ
class SearchKeyword(BaseModel):
    keyword: str = Field(description="คำสำคัญที่ได้จากการประมวลผลคำถาม")

# ฟังก์ชัน Clean keyword
def clean_keyword(keyword: str) -> str:
    unwanted_words = ["แถวนี้", "ใกล้ฉัน", "ใกล้", "ช่วยหา"]
    for word in unwanted_words:
        keyword = keyword.replace(word, "")
    return re.sub(r'\s+', ' ', keyword).strip()

# ฟังก์ชันสำหรับค้นหาผ่าน Logdo Map API
def search_logdo_map_api(keyword, user_location, radius):
    base_url = "https://search.longdo.com/mapsearch/json/search?"
    lat, lon = user_location  # user_location = (latitude, longitude)

    params = {
        'keyword': keyword,
        'lat': lat,  # ส่งพิกัดที่อยู่
        'lon': lon,
        'span': radius,  # ระยะรัศมี
        'locale': 'th',
        'key': '7b6f8a4c53a57fa8315fbdcf5b108c83'  # ใส่ API Key logdo mapที่ถูกต้อง
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        try:
            data = response.json()  # พยายามแปลงเป็น JSON
            # print("ข้อมูลที่ได้รับจาก API:", data)  # แสดงข้อมูลจาก API
            return data
        except requests.exceptions.JSONDecodeError:
            print("Error: Response is not a valid JSON.")
            print("Response Text:", response.text)  # แสดงข้อความที่ได้จาก API
            return None
    else:
        print(f"Error: API returned status code {response.status_code}.")
        return None

# ฟังก์ชันสำหรับประมวลผลคำถามของผู้ใช้
def process_user_query(user_query, user_location, radius):
    # ตรวจสอบว่า user_query, user_location และ radius มีค่าไหม
    if not user_query or not user_location or not radius:
        return None, "Please provide valid inputs for location, radius, and search query."
    
    parser = JsonOutputParser(pydantic_object=SearchKeyword)
    prompt = PromptTemplate(
        template="""## คุณมีหน้าที่กรองคำสำคัญจากคำขอผู้ใช้.
        # คำขอผู้ใช้: {user_query}
        # Your response should be structured as follows:
        {format_instructions}""",
        input_variables=["user_query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser
    event = chain.invoke({"user_query": user_query, "user_location": user_location})

    if event:
        keyword = event.get('keyword', '')
        cleaned_keyword = clean_keyword(keyword)
        if cleaned_keyword:
            places_from_api = search_logdo_map_api(cleaned_keyword, user_location, radius)
            return cleaned_keyword, places_from_api
        else:
            return None, "Unable to clean keyword or no places found."
    return None, "No event data returned from LLM."

def find_route(places_interest,user_location,user_destination,radius):
    
    # keyword = process_places_of_interest_routes(places_of_interest)
    # if not keyword:
    #     return None  # จัดการกรณีที่ไม่มีคำหลัก
    
    # flon, flat, tlon, tlat = convert_locations(user_location, user_destination)
    # route_data, places_of_interest = get_places_from_route(flon, flat, tlon, tlat, keyword, radius)
    
    # if not route_data:
    #     return None  # จัดการกรณีไม่สามารถดึงข้อมูลเส้นทางได้
    
    # # จากนั้นคุณสามารถเรียงลำดับจุดเส้นทางตามระยะทางหรือเกณฑ์อื่น
    # sorted_route_points = sort_points([place['coordinates'] for place in places_of_interest], user_location)
    
    # # แสดงผลเส้นทางและสถานที่บนแผนที่
    # create_map(route_data, places_of_interest, user_location, user_destination, sorted_route_points)
    return 

def create_tool():
    keep = []
    getquery = process_user_query 
    getroute = find_route 
             
    tool_api = StructuredTool.from_function(
        func=getquery,
        name="query_place",
        description="สำหรับค้นหาสถานที่บริเวณรอบตัว user_query คำค้นหา, user_location ตำแหน่งของเรา, radius รัศมี",
    )
    tool_route = StructuredTool.from_function(
        func=getroute,
        name="find_route",
        description="หาเส้นไปยังสถานที่ที่กำหนด start เริ่ม, end ที่หา",
    ) 
    keep.append(tool_api)
    keep.append(tool_route)   
    return keep
 

# ฟังก์ชันสำหรับแสดงรายชื่อสถานที่
def display_places_list(places_data):
    if places_data and "data" in places_data:
        places = places_data["data"]

        # ส่วนของ Header ที่ครอบข้อมูลสถานที่ทั้งหมด
        st.header('รายชื่อสถานที่')

        # สร้าง container ที่สามารถเลื่อนดูได้
        with st.container():
            # สร้าง div สำหรับส่วนที่เลื่อนดูทั้งหมด
            st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
            
            # แสดงรายการสถานที่ต่างๆ ด้านใน container ที่สามารถเลื่อนดูได้
            for place in places:
                # สร้าง block สำหรับรายละเอียดสถานที่
                with st.expander(f"ดูรายละเอียด: {place.get('name', 'สถานที่')}"):
                    st.markdown('<div class="place-item">', unsafe_allow_html=True)
                    st.write(f"**ชื่อสถานที่:** {place.get('name', 'ไม่ทราบชื่อ')}")
                    st.write(f"**ที่อยู่:** {place.get('address', 'ไม่ทราบที่อยู่')}")
                    st.write(f"**โทรศัพท์:** {place.get('tel', 'ไม่มีข้อมูล')}")
                    st.write(f"**ระยะทาง:** {place.get('distance', 'ไม่ระบุ')} km")
                    st.write(f"**ละติจูด:** {place.get('lat', 'ไม่มีข้อมูลพิกัดตำแหน่ง')}")
                    st.write(f"**ลองจิจูด:** {place.get('lon', 'ไม่มีข้อมูลพิกัดตำแหน่ง')}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.write("ไม่พบข้อมูลสถานที่ในผลลัพธ์")

#  ฟังก์ชันสร้างแผนที่และแสดงสถานที่
def create_and_display_map(places_data, user_location=None):
    if not places_data or "data" not in places_data:
        st.write("ไม่พบข้อมูลสถานที่")
        return

    places = places_data["data"]
    
    # ตรวจสอบว่ามีสถานที่ที่มีพิกัดหรือไม่
    if not any(place.get("lat") and place.get("lon") for place in places):
        st.write("ไม่พบข้อมูลพิกัดของสถานที่")
        return

    # ใช้พิกัดของผู้ใช้เป็นจุดศูนย์กลางแผนที่
    if user_location:
        center_lat, center_lon = user_location
    else:
        # ถ้าไม่มีพิกัดของผู้ใช้ ให้คำนวณค่าเฉลี่ยจากสถานที่ที่กรองมา
        latitudes = [place.get("lat") for place in places if place.get("lat")]
        longitudes = [place.get("lon") for place in places if place.get("lon")]
        if latitudes and longitudes:
            center_lat = sum(latitudes) / len(latitudes)
            center_lon = sum(longitudes) / len(longitudes)
        else:
            st.write("ไม่สามารถคำนวณจุดศูนย์กลางจากสถานที่")
            return
    
    # สร้างแผนที่
    m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

    # เพิ่ม marker สำหรับสถานที่ที่กรองมา
    for place in places:
        lat = place.get("lat")
        lon = place.get("lon")
        if lat and lon:
            name = place.get("name", "ไม่ทราบชื่อ")
            folium.Marker([float(lat), float(lon)],
                          popup=name,
                          icon=folium.Icon(color="green")).add_to(m)

    # เพิ่ม marker สำหรับตำแหน่งของผู้ใช้ (ถ้ามี)
    if user_location:
        folium.Marker([user_location[0], user_location[1]],
                      popup="คุณอยู่ที่นี่",
                      icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)

    # แสดงแผนที่ใน Streamlit
    html(m._repr_html_(), height=500)

# ฟังก์ชันสำหรับแสดงคำแนะนำสถานที่
def display_recommendations(places_data, user_query=None):
    if not places_data or "data" not in places_data:
        print("ไม่พบข้อมูลสถานที่")
        return

    # จำกัดสถานที่ให้แสดงเพียง 5 แห่ง
    places = places_data["data"][:5]

    # ตรวจสอบว่ามีข้อมูลสถานที่หรือไม่
    if not places:
        print("ไม่มีสถานที่สำหรับการแนะนำ")
        return

    # สร้างคำอธิบายสถานที่
    places_description = "\n".join([
        f"{index + 1}. {place.get('name', 'ไม่ทราบชื่อ')} - {place.get('address', 'ไม่มีที่อยู่')}"
        for index, place in enumerate(places)
    ])

    # สร้างคำสั่งสำหรับ LLM
    prompt = f"""
    ต่อไปนี้คือสถานที่ที่พบจากคำค้นหา: "{user_query}"
    
    {places_description}
    
    กรุณาเปรียบเทียบสถานที่เหล่านี้ โดยระบุข้อดีและข้อเสียของแต่ละสถานที่ รวมถึงแนะนำสถานที่ที่เหมาะสมที่สุดสำหรับผู้ใช้งาน.
    """

    # ส่งคำสั่งไปยัง LLM
    try:
        response = llm.invoke(prompt)
        # แสดงผลคำแนะนำจาก LLM
        st.subheader("Recommendation:")
        st.write(response.content.strip())
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์ข้อมูล: {str(e)}")

# ฟังก์ชันหลักสำหรับการค้นหาและแสดงผล
def main(user_query, user_location, radius):
    keyword, places_from_api = process_user_query(user_query, user_location, radius)
    if keyword:
        # print(f"คำค้นหา: {keyword}")
        display_places_list(places_from_api)
        create_and_display_map(places_from_api, user_location)
    else:
        print("ไม่พบคำสำคัญจากการประมวลผล")