# Import Modules
from turtle import st
from langchain_openai import ChatOpenAI
import pandas as pd
from geopy.distance import geodesic
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import re
import ipywidgets as widgets
import folium
from IPython.display import display
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

llm = ChatOpenAI(
    model='gpt-4o-mini',
    base_url= os.getenv("url"),  
    api_key= os.getenv("api_key"),  
    max_tokens=1000  
)

# 2. โหลดข้อมูล
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df.dropna(subset=['LATITUDE_LOCATION', 'LONGITUDE_LOCATION'])

# 3. คำนวณระยะทางระหว่างตำแหน่งผู้ใช้กับสถานที่ใน DataFrame
def calculate_distance(user_location, place_location):
    return geodesic(user_location, place_location).kilometers

# 4. ใช้ LLM เพื่อแยกคำสำคัญจากคำถามของผู้ใช้
def extract_keywords_from_query(llm, query):
    response = llm.invoke(f"แยกคำสำคัญจากคำถามนี้: '{query}' และแสดงคำสำคัญที่เกี่ยวข้องที่สามารถใช้กรองข้อมูลได้")
    return response.content.strip()

# 5. กรองข้อมูลตามระยะทาง
def filter_data_by_distance(df, user_location, radius):
    df['DISTANCE'] = df.apply(
        lambda row: calculate_distance(user_location, (row['LATITUDE_LOCATION'], row['LONGITUDE_LOCATION'])), 
        axis=1
    )
    filtered = df[df['DISTANCE'] <= radius]
    return filtered.sort_values(by='DISTANCE', ascending=True)

# 6. กรองข้อมูลด้วย Prompt Engineering
class ScheduleEvent(BaseModel):
    Names: list[str] = Field(description="คือ list สถานที่ท่องเที่ยว")

def filter_data_by_categories(llm, user_query, unique_attr_sub_types, sorted_filtered_df):
    parser = JsonOutputParser(pydantic_object=ScheduleEvent)
    
    prompt = PromptTemplate(
        template="""\
## คุณมีหน้าที่กรองประเภทจากคำขอผู้ใช้.

# คำขอผู้ใช้: {user_query}
## สถานที่ ท่องเที่ยวทั้งหมดที่มี เลือกจากในนี้มาตอบเท่านั้น และหากไม่มีสถานที่ตรงกับประภทจากคำขอผู้ใช้ ให้แสดงประภทที่ใกล้เคียง: 
{unique_attr_sub_types}

# Your response should be structured as follows:
{format_instructions}
""",
        input_variables=["user_query", "unique_attr_sub_types"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    event = chain.invoke({"user_query": user_query, "unique_attr_sub_types": unique_attr_sub_types})
    categories_to_filter = event['Names']

    if categories_to_filter:
        pattern = "|".join(map(re.escape, categories_to_filter))
        return sorted_filtered_df[sorted_filtered_df['ATTR_SUB_TYPE_TH'].str.contains(pattern, na=False)].head(5)
    return pd.DataFrame()

# 7,8 ฟังก์ชันสร้างแผนที่และแสดงสถานที่
def create_and_display_map(filtered_df, user_location=None):
    # ใช้พิกัดของผู้ใช้เป็นจุดศูนย์กลางแผนที่
    center_lat, center_lon = user_location if user_location else (filtered_df['LATITUDE_LOCATION'].mean(), filtered_df['LONGITUDE_LOCATION'].mean())
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    # เพิ่ม marker สำหรับสถานที่ที่กรองมา
    for _, row in filtered_df.iterrows():
        folium.Marker([row['LATITUDE_LOCATION'], row['LONGITUDE_LOCATION']],
                      popup=row['ATT_NAME_TH'],
                      icon=folium.Icon(color="green")).add_to(m)
    
    # เพิ่ม marker สำหรับตำแหน่งของผู้ใช้ (ถ้ามี)
    if user_location:
        folium.Marker([user_location[0], user_location[1]],
                      popup="คุณอยู่ที่นี่",
                      icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)

    # แสดงแผนที่ใน Streamlit
    components.html(m._repr_html_(), height=500)

# 9. แนะนำสถานที่ท่องเที่ยวและเปรียบเทียบ
def generate_recommendation(llm, df):
    places_info = df[['ATT_NAME_TH', 'ATTR_SUB_TYPE_TH', 'LATITUDE_LOCATION', 'LONGITUDE_LOCATION', 'ATT_DETAIL_TH', 'DISTANCE']]
    places_description = "\n".join([f"{index+1}. สถานที่: {row['ATT_NAME_TH']}\n"
                                   f"   ประเภท: {row['ATTR_SUB_TYPE_TH']}\n"
                                   f"   ระยะทาง: {row['DISTANCE']:.2f} กม.\n"
                                   f"   รายละเอียด: {row['ATT_DETAIL_TH']}\n"
                                   for index, row in places_info.iterrows()])
    
    prompt = f"""
    ต่อไปนี้คือสถานที่ท่องเที่ยว 5 แห่งที่กรองมาแล้วจากข้อมูลในพื้นที่ใกล้เคียง:
    
    {places_description}
    
    กรุณาให้ข้อมูลเพิ่มเติมเกี่ยวกับแต่ละสถานที่ เช่น ความสะดวกในการเดินทาง, ความนิยม, และบริการต่างๆ ที่อาจมีให้ในแต่ละแห่ง โดยไม่ต้องสรุปเป็นข้อดีข้อเสีย.
    คำแนะนำของคุณจะช่วยในการตัดสินใจเลือกสถานที่ท่องเที่ยวที่เหมาะสมที่สุด.
    """
    response = llm.invoke(prompt)
    return response.content.strip()

# Main Execution Example
if __name__ == "__main__":
    # ตรวจสอบว่าไฟล์มีการอัปโหลดหรือยัง
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    
    # ถ้าอัปโหลดไฟล์ใหม่ ใช้ไฟล์ที่อัปโหลด
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        function_df = pd.read_csv(uploaded_file)  # ใช้ไฟล์ที่อัปโหลดเป็น function_CSV
    else:
        # ถ้าไม่มีการอัปโหลด ให้ใช้ไฟล์ function_CSV.csv และ splitData.csv
        df = load_data("splitData.csv")
        function_df = pd.read_csv('function_CSV.csv')  # โหลด function_CSV.csv ที่มีในโค้ด
    
    user_location = (function_df.loc[0, 'user_lat'], function_df.loc[0, 'user_lon'])  # พิกัดของผู้ใช้
    radius = function_df.loc[0, 'radius']  # รัศมี
    user_query = function_df.loc[0, 'user_query']  # คำถามของผู้ใช้

    # Filter by distance
    sorted_filtered_df = filter_data_by_distance(df, user_location, radius)

    # Extract and filter categories
    unique_attr_sub_types = sorted_filtered_df['ATTR_SUB_TYPE_TH'].drop_duplicates().tolist()
    filtered_df = filter_data_by_categories(llm, user_query, unique_attr_sub_types, sorted_filtered_df)

    # Map display
    if not filtered_df.empty:
        dropdown = widgets.Dropdown(
            options=filtered_df['ATT_NAME_TH'].tolist(),
            description='สถานที่:',
            value=filtered_df['ATT_NAME_TH'].iloc[0]
        )
        display(widgets.VBox([dropdown]))
        create_and_display_map(filtered_df, dropdown, user_location)

    # Generate recommendations
    if not filtered_df.empty:
        recommendation = generate_recommendation(llm, filtered_df.head(5))
        print(recommendation)