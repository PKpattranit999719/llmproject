import streamlit as st
import requests

api_key = "7b6f8a4c53a57fa8315fbdcf5b108c83"

# ฟังก์ชันดึงข้อมูลจาก Longdo API
def get_address_from_longdo(api_key, poi_required=True, language='th'):
    url = f"https://api.longdo.com/map/?key={api_key}"
    params = {
        'language': language,
        'poi_required': poi_required,
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            else:
                return f"Error: Response is not in JSON format."
        else:
            return f"Error: Received status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def chat_with_api():
    st.subheader("Chat with API Data")
    st.write("You selected Chat using API Data.")

    # ใช้ session_state เพื่อเก็บข้อมูลที่กรอก
    if 'user_address' not in st.session_state:
        st.session_state.user_address = ""

    # เมื่อกดปุ่ม "Click here to get your location"
    if st.button("Click here to get your location", key="location_button"):
        with st.expander("Location Details"):
            st.write("Here you can display additional details or interact with the user.")

            # รับข้อมูลจากผู้ใช้
            name = st.text_input("Enter your Address:", value=st.session_state.user_address)

            # แสดงข้อมูลที่ผู้ใช้กรอก
            if name:
                st.write(f"You entered: {name}")  # แสดงข้อมูลที่กรอกโดยผู้ใช้

                # เก็บค่าใน session_state เพื่อให้มันคงอยู่
                st.session_state.user_address = name

                # เรียกใช้ API
                address_data = get_address_from_longdo(api_key)
                if address_data:
                    st.write("Address data from Longdo API:")
                    st.json(address_data)  # แสดงข้อมูลที่ได้จาก API

# เรียกใช้ฟังก์ชัน
if __name__ == "__main__":
    chat_with_api()
