import streamlit as st
from function_api import find_route
from function_csv import load_data, filter_data_by_distance, filter_data_by_categories, generate_recommendation, create_and_display_map  # Import ฟังก์ชันจากไฟล์ function_csv
from langchain_openai import ChatOpenAI
import requests
import urllib.parse
from langchain_core.prompts import PromptTemplate
import re

url = 'http://111.223.37.52/v1'
api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7Im9yZ2FuaXphdGlvbl9pZCI6IjY3NjhkNzA3YjNiYmM5MWQwYWNjMWNjNCIsInRva2VuX25hbWUiOiJCYW5rIiwic3RkRGF0ZSI6IjIwMjUtMDEtMTlUMTc6MDA6MDAuMDAwWiJ9LCJpYXQiOjE3MzczNTkxMDcsImV4cCI6MTc0MDU4OTE5OX0.7peNsGJSnQL2tctiui3MXTBc5OZsLv8OSizh68KVH5w'

llm = ChatOpenAI(
    model='gpt-4o-mini',
    base_url=url,  
    api_key=api_key,  
    max_tokens=1000  
)

def classify_question(user_query):
    prompt = PromptTemplate(
        template="""ช่วยแยกประเภทคำถามนี้: {user_query}.
                    ให้ตอบเพียงคำเดียว:
                    - "place" ถ้าคำถามเกี่ยวกับการค้นหาสถานที่
                    - "route" ถ้าคำถามเกี่ยวกับเส้นทางการเดินทาง
                    - "unknown" ถ้าคำถามไม่สามารถแยกประเภทได้""",
        input_variables=["user_query"]
    )
    
    # สร้าง prompt โดยการใช้ format
    formatted_prompt = prompt.format(user_query=user_query)
    
    # ส่งคำถามไปยัง LLM และรับคำตอบ
    response = llm.invoke(formatted_prompt)
    
    # แสดงข้อมูลสำหรับดีบัก
    st.write(f"LLM Response (Raw): {response.content}")
    
    # ทำความสะอาดคำตอบ
    cleaned_response = response.content.strip().lower()
    
    # ใช้ regex เพื่อจับคำตอบที่เป็นเพียง "place", "route", หรือ "unknown"
    match = re.search(r'\b(place|route|unknown)\b', cleaned_response)
    
    if match:
        result = match.group(1)  # ดึงคำที่ตรงกับ pattern
    else:
        result = "unknown"  # กรณีที่ไม่มีคำตอบที่ถูกต้อง
    
    # แสดงผลที่ทำความสะอาดแล้ว
    st.write(f"LLM Response (Cleaned & Matched): {result}")
    
    return result

# ฟังก์ชัน Chat ที่จะรับข้อความจากผู้ใช้และตอบกลับ
def chat_with_csv():
    st.subheader("Chat with CSV Data")
    st.write("You selected Chat using CSV Data.")

    # ใช้ session_state เพื่อเก็บประวัติการสนทนา
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # แสดงประวัติการสนทนา
    for message in st.session_state.messages:
        st.write(f"**{message['role']}**: {message['content']}")
        
    user_query = st.text_input("กรุณากรอกคำถามของคุณ:")

    if user_query:
        # ใช้ LLM ในการแยกประเภทคำถาม
        question_type = classify_question(user_query)
        
        if question_type == "route":
            st.header("กรอกข้อมูลสำหรับเส้นทาง")
            user_location = st.text_input("Enter your location (latitude, longitude):", key="location_input")
            user_destination = st.text_input("Enter destination location (latitude, longitude):", key="destination_input")
   
            with st.expander("How to get your location with Google Maps?"):
                st.write("""
                1. Open Google Maps on your device.
                2. Right-click on your desired location and select **"What's here?"**.
                3. Copy the latitude and longitude displayed at the bottom of the screen.
                """)
                st.markdown(
                    "Visit Google Maps: [Click here](https://www.google.com/maps/)",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    """
                    <style>
                        .small-link {
                            font-size: 14px; /* กำหนดขนาดตัวอักษร */
                        }
                    </style>
                    <a href="https://www.iphone-droid.net/how-to-get-the-coordinates-or-search-by-latitude-longitude-on-google-maps/" class="small-link">
                        This link provides detailed instructions on how to perform this action.
                    </a>
                    """,
                    unsafe_allow_html=True,
                )
            with st.expander("Find your location?"):
                # ส่วนต้อนรับและรับค่าจากผู้ใช้
                st.subheader("Find Latitude and Longitude of a Location")
                # รับค่าชื่อสถานที่จากผู้ใช้
                searched_location = st.text_input("Enter your searched location:")

                if st.button("Search", key="search_button"):
                    if searched_location:  # ตรวจสอบว่าผู้ใช้กรอกข้อมูล
                        # สร้าง URL สำหรับการค้นหาด้วย Nominatim API
                        url = f'https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(searched_location)}&format=json'
                        
                        headers = {
                            'User-Agent': 'MyGeocodingApp/1.0'  # ใส่ User-Agent เพื่อระบุตัวตน
                        }

                        # ส่งคำขอไปยัง Nominatim API
                        response = requests.get(url, headers=headers)

                        if response.status_code == 200:
                            data = response.json()
                            if data:  # ตรวจสอบว่ามีผลลัพธ์
                                latitude = data[0]["lat"]
                                longitude = data[0]["lon"]
                                st.success("Location found!")
                                st.write(f"**Latitude:** {latitude}")
                                st.write(f"**Longitude:** {longitude}")
                            else:
                                st.error("No results found for the given location.")
                        else:
                            st.error(f"Error: {response.status_code}")
                    else:
                        st.warning("Please enter a location to search.")
                
            radius = st.number_input("Enter the search radius (in meter):", min_value=1, max_value=200, value=150, key="radius_input")
            search_query = st.text_input("Enter your search query (e.g., 'อยากเดินทางจากพระราม9ไปวัดพระแก้ว', 'จากกรุงเทพไปกำแพงแสน'):", value=user_query, key="search_input")
            places_interest = st.text_input("Enter your place interest(สถานที่ที่อยากแวะ หรือ สนใจระหว่างทาง e.g.'ต้องการทานข้าวหรือแวะพักทานอาหาร')", key="places_interest")
            
        elif question_type == "place":
            st.header("กรอกข้อมูลสำหรับการค้นหาสถานที่")   
            user_location = st.text_input("Enter your location (latitude, longitude):", key="location_input")
    
            with st.expander("How to get your location with Google Maps?"):
                st.write("""
                1. Open Google Maps on your device.
                2. Right-click on your desired location and select **"What's here?"**.
                3. Copy the latitude and longitude displayed at the bottom of the screen.
                """)
                st.markdown(
                    "Visit Google Maps: [Click here](https://www.google.com/maps/)",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    """
                    <style>
                        .small-link {
                            font-size: 14px; /* กำหนดขนาดตัวอักษร */
                        }
                    </style>
                    <a href="https://www.iphone-droid.net/how-to-get-the-coordinates-or-search-by-latitude-longitude-on-google-maps/" class="small-link">
                        This link provides detailed instructions on how to perform this action.
                    </a>
                    """,
                    unsafe_allow_html=True,
                )
            with st.expander("Find your location?"):
                # ส่วนต้อนรับและรับค่าจากผู้ใช้
                st.subheader("Find Latitude and Longitude of a Location")
                # รับค่าชื่อสถานที่จากผู้ใช้
                searched_location = st.text_input("Enter your searched location:")

                if st.button("Search", key="search_button"):
                    if searched_location:  # ตรวจสอบว่าผู้ใช้กรอกข้อมูล
                        # สร้าง URL สำหรับการค้นหาด้วย Nominatim API
                        url = f'https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(searched_location)}&format=json'
                        
                        headers = {
                            'User-Agent': 'MyGeocodingApp/1.0'  # ใส่ User-Agent เพื่อระบุตัวตน
                        }

                        # ส่งคำขอไปยัง Nominatim API
                        response = requests.get(url, headers=headers)

                        if response.status_code == 200:
                            data = response.json()
                            if data:  # ตรวจสอบว่ามีผลลัพธ์
                                latitude = data[0]["lat"]
                                longitude = data[0]["lon"]
                                st.success("Location found!")
                                st.write(f"**Latitude:** {latitude}")
                                st.write(f"**Longitude:** {longitude}")
                            else:
                                st.error("No results found for the given location.")
                        else:
                            st.error(f"Error: {response.status_code}")
                    else:
                        st.warning("Please enter a location to search.")
                        
            radius = st.number_input("Enter the search radius (in kilometers):", min_value=1, max_value=100, value=10, key="radius_input")
            search_query = st.text_input("Enter your search query (e.g., 'ช่วยหาแหล่งท่องเที่ยวทางธรรมชาติ', 'พิพิธภัณฑ์'):",value=user_query, key="search_input")
    
        if st.button("Search"):
            if question_type == "place":
            # เก็บข้อความจากผู้ใช้
                user_message = f"Location: {user_location}, Radius: {radius} km, Search Query: {search_query}"
                st.session_state.messages.append({"role": "User", "content": user_message})

                # ตรวจสอบว่า user_location มีข้อมูลหรือไม่
                if user_location and radius and search_query:
                    # แยกตำแหน่งจากข้อความ (เช่น "14.022788, 99.978337" เป็น tuple (14.022788, 99.978337))
                    user_lat, user_lon = map(float, user_location.split(","))

                    if "uploaded_df" in st.session_state:
                        df = st.session_state["uploaded_df"]  # ใช้ข้อมูลจากไฟล์ที่อัปโหลด
                    else:
                        df = load_data("C:/llmproject/Map_project/splitData.csv")  # ใช้ไฟล์เดิมหากไม่มีการอัปโหลด

                    # กรองข้อมูลตามระยะทาง
                    sorted_filtered_df = filter_data_by_distance(df, (user_lat, user_lon), radius)

                    # กรองข้อมูลด้วยคำค้นหาจากผู้ใช้
                    unique_attr_sub_types = sorted_filtered_df['ATTR_SUB_TYPE_TH'].drop_duplicates().tolist()
                    filtered_df = filter_data_by_categories(llm, search_query, unique_attr_sub_types, sorted_filtered_df)

                # ถ้ามีข้อมูลที่กรองแล้ว
                if not filtered_df.empty:
                    system_reply = f"Found {len(filtered_df)} places matching your search query: {search_query} within {radius} km of {user_location}."
                    st.session_state.messages.append({"role": "System", "content": system_reply})
                    #st.write(system_reply)

                    # แสดงแผนที่ทั้งหมด
                    create_and_display_map(filtered_df, user_location=(user_lat, user_lon))

                    # แสดงคำแนะนำ
                    st.write("**Recommendation for places to visit:**")

                    # ใช้ expander เพื่อแสดงข้อมูลสำหรับแต่ละสถานที่
                    for index, row in filtered_df.head(5).iterrows():
                        place_name = row['ATT_NAME_TH']
                        place_type = row['ATTR_SUB_TYPE_TH']
                        distance = row['DISTANCE']
                        place_details = row['ATT_DETAIL_TH']

                        # สร้าง expander สำหรับแต่ละสถานที่
                        with st.expander(f"Place {index + 1}: {place_name}"):
                            st.markdown(f"**ประเภท**: {place_type}")
                            st.markdown(f"**ระยะทาง**: {distance:.2f} กม.")
                            st.markdown(f"**รายละเอียด**: {place_details}")

                    # เรียกใช้ฟังก์ชันแนะนำจาก LLM สำหรับสถานที่ทั้งหมดที่กรองมา
                    recommendation = generate_recommendation(llm, filtered_df.head(5)) 

                    # แสดงคำแนะนำรวมจาก LLM
                    st.subheader("Recommendation:")
                    with st.expander("📍 คำแนะนำสถานที่จาก LLM"):
                        st.write("นี่คือสถานที่ที่แนะนำตามเส้นทางของคุณ:")
                        st.markdown(recommendation)

                    
                else:
                    system_reply = f"No places found matching your search query: {search_query} within {radius} km of {user_location}."
                    st.session_state.messages.append({"role": "System", "content": system_reply})
                    st.write(system_reply)
               
            elif question_type == "route":
                # ตรวจสอบค่าต่างๆ ว่ามีหรือไม่
                if not user_location or not radius or not search_query or not user_destination:
                    st.session_state.messages.append({"role": "System", "content": "Please provide valid inputs for location, radius, search query, and destination."})
                    return
                
                # เก็บข้อความจากผู้ใช้
                user_message = f"Location: {user_location}, Radius: {radius} km, Search Query: {search_query}, Destination: {user_destination}"
                st.session_state.messages.append({"role": "User", "content": user_message})

                # แยกตำแหน่งจากข้อความ (เช่น "14.022788, 99.978337" เป็น tuple (14.022788, 99.978337))
                try:
                    user_lat, user_lon = map(float, user_location.split(","))
                    destination_lat, destination_lon = map(float, user_destination.split(","))
                except ValueError:
                    st.session_state.messages.append({"role": "System", "content": "Invalid location or destination format. Please enter latitude, longitude."})
                    return

                # เรียกใช้ฟังก์ชัน find_route สำหรับการค้นหาเส้นทางและสถานที่ที่น่าสนใจ
                result = find_route(places_interest, (user_lat, user_lon), (destination_lat, destination_lon), radius)
                
                if result:
                    route_data, places_of_interest = result
                    if not route_data or not places_of_interest:
                        system_reply = f"No route or places of interest found matching your search query: '{search_query}' within {radius} km of {user_location}."
                        st.session_state.messages.append({"role": "System", "content": system_reply})
                        st.write(system_reply)
                    else:
                        system_reply = f"Found route and places of interest matching your search query: '{search_query}' within {radius} km of {user_location}."
                        st.session_state.messages.append({"role": "System", "content": system_reply})
                        st.write(system_reply)
                else:
                    system_reply = "Unable to find a valid route or places of interest."
                    st.session_state.messages.append({"role": "System", "content": system_reply})
                    st.write(system_reply) 
                      
# เรียกใช้ฟังก์ชัน chat_with_csv ใน Streamlit
if __name__ == "__main__":
    chat_with_csv()
