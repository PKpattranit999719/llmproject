import streamlit as st
from Map_project.function_routes import (
    convert_locations, display_route_explanation, explain_route_with_llm, 
    extract_and_analyze_data, get_places_from_route, process_places_of_interest_routes, 
    search_places_of_interest, create_map, recommend_places
)

# หัวข้อหน้าเว็บ
st.title("Test Function Routes")
places_interest = "อยากกินข้าว"
user_location = (13.7563, 100.5018)  # จุดเริ่มต้น กรุงเทพฯ
user_destination = (14.022788, 99.978337)  # จุดสิ้นสุด กาญจนบุรี
radius = 5  # รัศมีการค้นหาสถานที่ 5 กิโลเมตร

# ใช้ฟังก์ชัน process_places_of_interest_routes ในการแยก keyword จาก query
keyword = process_places_of_interest_routes(places_interest)
st.write(f"Extracted Keyword: {keyword}")  # เช็คค่า keyword ที่ได้

# 1. ส่งค่าพิกัดเริ่มต้นและปลายทางเพื่อหาข้อมูลเส้นทาง
flon, flat, tlon, tlat = convert_locations(user_location, user_destination)
route_data = {'flon': flon, 'flat': flat, 'tlon': tlon, 'tlat': tlat, 'keyword': keyword, 'radius': radius}
st.write(f"Route Data: {route_data}")  # ตรวจสอบค่าพิกัดที่ใช้

# 2. ใช้ข้อมูลเส้นทางในการหาสถานที่ที่เกี่ยวข้อง
places_with_coordinates = get_places_from_route(route_data)
st.write(f"Places with Coordinates: {places_with_coordinates}")  # ตรวจสอบค่าพิกัดสถานที่

# 3. ค้นหาสถานที่ตาม keyword จากเส้นทาง
places_of_interest = search_places_of_interest(flon, flat, tlon, tlat, keyword, radius)
st.write(f"Places of Interest: {places_of_interest}")  # ตรวจสอบสถานที่ที่ได้

# 4. แสดงแผนที่
create_map(route_data, places_of_interest, user_location, user_destination, places_with_coordinates)

# 5. แนะนำสถานที่ด้วย LLM
recommendations = recommend_places(places_of_interest, keyword, top_n=10)
st.write(f"Recommendations: {recommendations}")  # ตรวจสอบคำแนะนำ

# 6. แสดงคำอธิบายเส้นทางการเดินทาง
explanation = explain_route_with_llm(route_data)
st.write(f"LLM Explanation: {explanation}")  # ตรวจสอบคำอธิบายจาก LLM
display_route_explanation(explanation)  # แสดงคำอธิบายการเดินทาง
