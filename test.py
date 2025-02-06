import json
import streamlit as st
from Map_project.function_routes import (
    DisplayMap, convert_locations, display_route_explanation, explain_route_with_llm, 
    get_route_data, get_route_path_from_id, process_places_of_interest_routes, 
    search_places_of_interest, recommend_places,extract_and_return_data_from_places
)

# หัวข้อหน้าเว็บ
st.title("Test Function Routes")
places_interest = "อยากกินข้าว"
user_location = (13.7563, 100.5018)  # จุดเริ่มต้น กรุงเทพฯ
user_destination = (14.022788, 99.978337)  # จุดสิ้นสุด กาญจนบุรี
radius = 1  # รัศมีการค้นหาสถานที่ 5 กิโลเมตร

# ใช้ฟังก์ชัน process_places_of_interest_routes ในการแยก keyword จาก query
keyword = process_places_of_interest_routes(places_interest)
st.write(f"Extracted Keyword: {keyword}")  # เช็คค่า keyword ที่ได้

# 1. ส่งค่าพิกัดเริ่มต้นและปลายทางเพื่อหาข้อมูลเส้นทาง
flon, flat, tlon, tlat = convert_locations(user_location, user_destination)

# # 2. ใช้ข้อมูลเส้นทางในการหาสถานที่ที่เกี่ยวข้อง
# status_placeholder = st.empty()  # สร้างที่ว่างสำหรับข้อความสถานะ
# with st.spinner("⏳ กำลังโหลดข้อมูล..."):
#     route_data = get_route_data(flon, flat, tlon, tlat)
#     places_with_coordinates = get_route_path_from_id(route_data)  # โหลดค่าจริงๆ
# print(places_with_coordinates)

# # # 3. ค้นหาสถานที่ตาม keyword จากเส้นทาง
# path = get_route_path_from_id(route_data['data'][0]['id'])
# places_of_interest = search_places_of_interest(path, keyword, radius)
# print(places_of_interest)
# # if places_of_interest:
# #     st.write(f"Places of Interest: {places_of_interest}")  # ตรวจสอบสถานที่ที่ได้
# # else:
# #     st.error("ไม่พบสถานที่ที่น่าสนใจตามคำค้นหาของคุณ")

status_placeholder = st.empty()  # สร้างที่ว่างสำหรับข้อความสถานะ
with st.spinner("⏳ กำลังโหลดข้อมูล..."):
    # 1. ดึงข้อมูลเส้นทางจากจุดเริ่มต้นและจุดหมายปลายทาง
    route_data = get_route_data(flon, flat, tlon, tlat)
    
    # 2. ใช้ข้อมูล route_data ไปหาเส้นทางโดยใช้ ID
    if route_data and 'data' in route_data:
        route_id = route_data['data'][0]['id']
        route_path_list = get_route_path_from_id(route_id)
        print("Route Path List:", route_path_list)

        # 3. ค้นหาสถานที่ที่น่าสนใจจากเส้นทาง
        places_of_interest = search_places_of_interest(route_path_list, keyword, radius)
        print("Places of Interest:", places_of_interest)
status_placeholder.text("การค้นหาสถานที่เสร็จสิ้นแล้ว")

# 4. แสดงแผนที่
extracted_data = extract_and_return_data_from_places(places_of_interest) 
# แสดงแผนที่ longdo map
route_markers = [
    { "lon": flon, "lat": flat, "title": "จุดเริ่มต้น"  },
    { "lon": tlon, "lat": tlat, "title": "จุดปลายทาง" }
]

poi_markers = [
    {"lon": place["place_lon"], "lat": place["place_lat"], "title": place["place_name"]}
    for place in extracted_data
]
# แปลงเป็น JSON
poi_markers_js = json.dumps(poi_markers, ensure_ascii=False)
route_markers_js = json.dumps(route_markers, ensure_ascii=False)

print("poi_markers_js",poi_markers_js)
print("route_markers_js",route_markers_js)

# เรียกใช้ฟังก์ชันแสดงแผนที่
DisplayMap(poi_markers_js, route_markers_js)

# 5. แสดงคำอธิบายเส้นทางการเดินทาง
explanation = explain_route_with_llm(route_data)
st.write(f"LLM Explanation: {explanation}")  # ตรวจสอบคำอธิบายจาก LLM
display_route_explanation(explanation)  # แสดงคำอธิบายการเดินทาง

# 6. แนะนำสถานที่ด้วย LLM
if poi_markers_js and places_of_interest:
    recommendations = recommend_places(poi_markers_js, places_of_interest, keyword)
    st.write("คำแนะนำสถานที่ที่ดีที่สุดจากเส้นทาง:")
    st.markdown(recommendations)  # แสดงคำแนะนำจาก LLM
else:
    st.warning("ไม่สามารถแนะนำสถานที่ได้เนื่องจากไม่มีข้อมูลที่เพียงพอ")

