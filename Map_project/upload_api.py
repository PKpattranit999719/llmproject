import streamlit as st

def upload_api():
    st.subheader("API KEY Data")
    st.write("Your API Key Data of Longdo Map.")
    
    # ลิงก์สำหรับไปที่หน้าเว็บของ Longdo Map เพื่อขอ API Key
    st.markdown(
        "Don't have an API Key? [Click here to get one from Longdo Map](https://map.longdo.com/products/)",
        unsafe_allow_html=True,
    )
    
    # รับค่า API Key จากผู้ใช้
    api_key = st.text_input("Enter the API Key:", type="password")  # ใช้ type="password" เพื่อไม่ให้แสดงค่า
    
    if api_key:
        st.write(f"API Key: {api_key}")
        
        # เพิ่มโค้ดการทำงานกับข้อมูลจาก API ที่นี่
        st.write("Here you can add your logic for interacting with API data.")
    else:
        st.warning("Please enter your API Key.")


        
