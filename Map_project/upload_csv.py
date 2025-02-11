import streamlit as st
import pandas as pd

def upload_csv():
    st.subheader("Upload CSV File")
    
    # ใช้ file uploader
    file = st.file_uploader("Upload CSV", type="csv")
    
    # เพิ่ม Expander สำหรับคำอธิบาย
    with st.expander("How to upload CSV file?"):
        st.write("""
        1. Click on the **Upload CSV** button.
        2. Choose a CSV file from your computer.
        3. Once the file is selected, the data will be displayed below.
        """)
    
    # อธิบายเกี่ยวกับคอลัมน์ในตาราง CSV
    with st.expander("CSV File Format Explanation"):
        st.write("""
        The CSV file should have the following columns:
        - **ATT_NAME_TH**: Name of the location in Thai.
        - **ATT_NAME_EN**: Name of the location in English.
        - **ATT_NEARBY_LOCATION**: Nearby locations.
        - **ATT_ADDRESS**: Address of the location.
        - **REGION_NAME_TH**: Name of the region in Thai.
        - **SUBDISTRICT_NAME_TH**: Name of the subdistrict in Thai.
        - **DISTRICT_NAME_TH**: Name of the district in Thai.
        - **PROVINCE_NAME_TH**: Name of the province in Thai.
        - **ATTR_CATAGORY_TH**: Category of the attribute in Thai.
        - **ATTR_SUB_TYPE_TH**: Subtype of the attribute in Thai.
        - **ATT_START_END**: Start and end times for the location.
        - **ATT_DETAIL_TH**: Detailed description in Thai.
        - **ATT_LOCATION**: GPS coordinates or specific location details.
        - **LATITUDE_LOCATION**: Latitude of the location.
        - **LONGITUDE_LOCATION**: Longitude of the location.
        """)

        # สร้างตารางตัวอย่าง
        data = {
            'ATT_NAME_TH': ['สถานที่ A', 'สถานที่ B'],
            'ATT_NAME_EN': ['Place A', 'Place B'],
            'ATT_NEARBY_LOCATION': ['สถานที่ C', 'สถานที่ D'],
            'ATT_ADDRESS': ['123/4, ถนน XYZ', '567/8, ถนน ABC'],
            'REGION_NAME_TH': ['ภาคเหนือ', 'ภาคใต้'],
            'SUBDISTRICT_NAME_TH': ['ตำบล A', 'ตำบล B'],
            'DISTRICT_NAME_TH': ['อำเภอ X', 'อำเภอ Y'],
            'PROVINCE_NAME_TH': ['จังหวัด A', 'จังหวัด B'],
            'ATTR_CATAGORY_TH': ['วัฒนธรรม', 'ธรรมชาติ'],
            'ATTR_SUB_TYPE_TH': ['มรดกโลก', 'น้ำตก'],
            'ATT_START_END': ['09:00 - 17:00', '08:00 - 18:00'],
            'ATT_DETAIL_TH': ['รายละเอียด A', 'รายละเอียด B'],
            'ATT_LOCATION': ['latitude, longitude', '14.5831377, 102.8053527'],
            'LATITUDE_LOCATION': [13.7275, 12.5643],
            'LONGITUDE_LOCATION': [100.5249, 101.6542]
        }

        # แสดงตารางตัวอย่าง
        df_example = pd.DataFrame(data)
        st.dataframe(df_example)

# เมื่อเลือกไฟล์
    if file is not None:
        df = pd.read_csv(file)

        # บันทึก DataFrame ลงใน session_state
        st.session_state["uploaded_df"] = df
        st.session_state["file_uploaded"] = True  # บันทึกสถานะว่าอัปโหลดแล้ว

        st.success("✅ อัปโหลดไฟล์สำเร็จ! ข้อมูลถูกบันทึกแล้ว")

        # ตรวจสอบว่ามีไฟล์อัปโหลดอยู่แล้วหรือไม่
    if "uploaded_df" in st.session_state:
        st.subheader("📊 ข้อมูลที่อัปโหลดล่าสุด")
        st.dataframe(st.session_state["uploaded_df"])
