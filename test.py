import streamlit as st
from Map_project.function_routes import (
    convert_locations, display_route_explanation, explain_route_with_llm, 
    get_places_from_route, get_route_data, process_places_of_interest_routes, 
    search_places_of_interest, create_map, recommend_places,extract_and_return_data_from_places
)

# หัวข้อหน้าเว็บ
st.title("Test Function Routes")
places_interest = "อยากกินข้าว"
user_location = (13.7563, 100.5018)  # จุดเริ่มต้น กรุงเทพฯ
user_destination = (14.022788, 99.978337)  # จุดสิ้นสุด กาญจนบุรี
radius = 2  # รัศมีการค้นหาสถานที่ 5 กิโลเมตร

# ใช้ฟังก์ชัน process_places_of_interest_routes ในการแยก keyword จาก query
keyword = process_places_of_interest_routes(places_interest)
st.write(f"Extracted Keyword: {keyword}")  # เช็คค่า keyword ที่ได้

# 1. ส่งค่าพิกัดเริ่มต้นและปลายทางเพื่อหาข้อมูลเส้นทาง
flon, flat, tlon, tlat = convert_locations(user_location, user_destination)

# 2. ใช้ข้อมูลเส้นทางในการหาสถานที่ที่เกี่ยวข้อง
status_placeholder = st.empty()  # สร้างที่ว่างสำหรับข้อความสถานะ
with st.spinner("⏳ กำลังโหลดข้อมูล..."):
    route_data = get_route_data(flon, flat, tlon, tlat)
    places_with_coordinates = get_places_from_route(route_data)  # โหลดค่าจริงๆ
print(places_with_coordinates)


# # 3. ค้นหาสถานที่ตาม keyword จากเส้นทาง
places_of_interest = search_places_of_interest(route_data, keyword, radius)
print(places_of_interest)
# if places_of_interest:
#     st.write(f"Places of Interest: {places_of_interest}")  # ตรวจสอบสถานที่ที่ได้
# else:
#     st.error("ไม่พบสถานที่ที่น่าสนใจตามคำค้นหาของคุณ")

# 4. แสดงแผนที่
if places_with_coordinates and places_of_interest:
    create_map(route_data, places_of_interest, user_location, user_destination, places_with_coordinates)
else:
    st.warning("ไม่สามารถแสดงแผนที่ได้เนื่องจากไม่มีข้อมูลที่จำเป็น")
#print(extracted_data)

# 5. แสดงคำอธิบายเส้นทางการเดินทาง
explanation = explain_route_with_llm(route_data)
st.write(f"LLM Explanation: {explanation}")  # ตรวจสอบคำอธิบายจาก LLM
display_route_explanation(explanation)  # แสดงคำอธิบายการเดินทาง

# 6. แนะนำสถานที่ด้วย LLM
if places_with_coordinates and places_of_interest:
    recommendations = recommend_places(places_with_coordinates, places_of_interest, keyword)
    st.write("คำแนะนำสถานที่ที่ดีที่สุดจากเส้นทาง:")
    st.markdown(recommendations)  # แสดงคำแนะนำจาก LLM
else:
    st.warning("ไม่สามารถแนะนำสถานที่ได้เนื่องจากไม่มีข้อมูลที่เพียงพอ")

