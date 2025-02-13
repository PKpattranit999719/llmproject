import streamlit as st
from upload_csv import upload_csv
from upload_api import upload_api
from chat_csv import chat_with_csv
from chat_api import chat_with_api

# ใช้ session_state เพื่อติดตามสถานะการเลือกเมนู
if 'page' not in st.session_state:
    st.session_state.page = "home"

# ใช้ session_state เพื่อติดตามสถานะการเริ่มใช้งาน
if 'started' not in st.session_state:
    st.session_state.started = False

# เพิ่ม title หลัก
st.title("SmartMap AI")

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "Home"  # เก็บเมนูที่เลือก

if st.session_state.get("started", False):
    st.sidebar.title("Main Menu")

    # ปุ่ม Home (ไม่มี selectbox)
    if st.sidebar.button("Home page"):
        st.session_state.selected_menu = "Home"
        st.session_state.page = "home"

    # ปุ่ม CSV (แสดง selectbox เฉพาะเมื่อเลือก CSV)
    if st.sidebar.button("Use CSV"):
        st.session_state.selected_menu = "CSV"

    if st.session_state.selected_menu == "CSV":
        csv_menu = st.sidebar.selectbox(
            "CSV Options",
            options=["Upload CSV", "Chat with CSV"]
        )
        if csv_menu == "Upload CSV":
            st.session_state.page = "upload_csv"
        elif csv_menu == "Chat with CSV":
            st.session_state.page = "chat_csv"

    # ปุ่ม API (แสดง selectbox เฉพาะเมื่อเลือก API)
    if st.sidebar.button("Use API"):
        st.session_state.selected_menu = "API"

    if st.session_state.selected_menu == "API":
        api_menu = st.sidebar.selectbox(
            "API Options",
            options=["API KEY", "Chat with API"]
        )
        if api_menu == "API KEY":
            st.session_state.page = "upload_api"
        elif api_menu == "Chat with API":
            st.session_state.page = "chat_api"

    
# Logic สำหรับการเปลี่ยนหน้า
if st.session_state.page == "home":
    
    # เพิ่มตัวเลือกการเลือกภาษา
    language = st.selectbox("Choose Language", options=["English", "Thai"])
    # เช็คภาษาและแสดงข้อความตามภาษา
    if language == "English":
        st.subheader("How to use this app")
        st.write("""
        Welcome to SmartMap AI! This app allows you to:
        - Upload and explore CSV data for location-based insights
        - Interact with CSV or API data via Chat for advanced queries
        - Upload your API Key for Longdo Map to enable map-based features such as:
            - Visualizing locations on a map
            - Calculating distances to points of interest
            - Searching for nearby locations within a specified radius
        """)
    
        # เพิ่มข้อความด้านล่างเพื่อแนะนำให้ใช้เมนูทางซ้าย
        st.write("Use the menu on the left to navigate through the features and get started.")
    
    if language == "Thai":
        st.subheader("วิธีการใช้งานแอปนี้")
        st.write("""
        ยินดีต้อนรับสู่ SmartMap AI! แอปนี้ช่วยให้คุณสามารถ:
        - อัปโหลดและสำรวจข้อมูล CSV เพื่อวิเคราะห์ข้อมูลเชิงสถานที่
        - โต้ตอบกับข้อมูล CSV หรือ API ผ่านการสนทนา (Chat) สำหรับการค้นหาและวิเคราะห์ขั้นสูง
        - อัปโหลด API Key ของ Longdo Map เพื่อเปิดใช้งานฟีเจอร์ที่เกี่ยวกับแผนที่ เช่น:
            - แสดงตำแหน่งบนแผนที่
            - คำนวณระยะทางไปยังสถานที่ที่คุณสนใจ
            - ค้นหาสถานที่ใกล้เคียงในรัศมีที่กำหนด
        """)
    
        # เพิ่มข้อความด้านล่างเพื่อแนะนำให้ใช้เมนูทางซ้าย
        st.write("ใช้เมนูทางด้านซ้ายเพื่อสำรวจฟีเจอร์ต่าง ๆ และเริ่มต้นใช้งาน")


elif st.session_state.page == "upload_csv":
    upload_csv()

elif st.session_state.page == "upload_api":
    upload_api()

elif st.session_state.page == "chat_csv":
    chat_with_csv()

elif st.session_state.page == "chat_api":
    chat_with_api()

# หากยังไม่เริ่มใช้งาน ให้แสดงคำอธิบายและปุ่มให้เริ่ม
if not st.session_state.started:
    start_button = st.button("Start Using the App")
    
    if start_button:
        st.session_state.started = True
        st.session_state.page = "home"  # ไปยังหน้า Home หรือหน้าอื่น ๆ
