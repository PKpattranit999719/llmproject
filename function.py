from langchain_openai import ChatOpenAI
import pandas as pd
from geopy.distance import geodesic
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import ipywidgets as widgets
import folium
from IPython.display import display
import re

# 1. Data Loading
def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads data from a CSV file into a pandas DataFrame.
    
    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the CSV file.
    """
    return pd.read_csv(file_path)

# 2. Distance Calculation
def calculate_distance(user_location, place_location) -> float:
    # ตรวจสอบว่า place_location มีค่าเป็น None หรือไม่
    if None in place_location or not all(isinstance(i, (int, float)) for i in place_location):
        return float('nan')  # ถ้าเป็น None ให้คืนค่า NaN
    try:
        return geodesic(user_location, place_location).kilometers
    except ValueError:
        return float('nan')  # ถ้าเกิดข้อผิดพลาดในการคำนวณระยะทาง ให้คืนค่า NaN

# 3. Keyword Extraction
def extract_keywords_from_query(query: str, llm: ChatOpenAI) -> str:
    """
    Uses the LLM model to extract keywords from a query.
    
    Args:
        query (str): The user's query to extract keywords from.
        llm (ChatOpenAI): The LLM model used to process the query.

    Returns:
        str: A string of extracted keywords.
    """
    response = llm.invoke(f"แยกคำสำคัญจากคำถามนี้: '{query}' และแสดงคำสำคัญที่เกี่ยวข้องที่สามารถใช้กรองข้อมูลได้")
    return response.content.strip()

# 4. Data Filtering by Distance
def filter_data_by_distance(df: pd.DataFrame, user_location: tuple, radius: float) -> pd.DataFrame:
    # ลบแถวที่ไม่มีข้อมูล LATITUDE_LOCATION หรือ LONGITUDE_LOCATION
    df = df.dropna(subset=['LATITUDE_LOCATION', 'LONGITUDE_LOCATION'])

    # คำนวณระยะทางระหว่างตำแหน่งของผู้ใช้และสถานที่
    df['DISTANCE'] = df.apply(
        lambda row: calculate_distance(user_location, (row['LATITUDE_LOCATION'], row['LONGITUDE_LOCATION'])),
        axis=1
    )
    
    # คัดกรองข้อมูลที่ระยะทางอยู่ภายในรัศมีที่กำหนด
    df = df[df['DISTANCE'] <= radius]
    
    # เรียงลำดับตามระยะทางจากน้อยไปหามาก
    df = df.sort_values(by='DISTANCE')
    
    return df

# 5. Prompt Engineering and Data Parsing
# กำหนดโครงสร้างของคำตอบที่เราคาดหวังจาก LLM
class ScheduleEvent(BaseModel):
    Names: list[str] = Field(description="คือ list สถานที่ท่องเที่ยว")

# ฟังก์ชันกรองสถานที่ตามคำขอจากผู้ใช้
def filter_places_to_query(user_query, unique_attr_sub_types, llm):
    # สร้าง parser
    parser = JsonOutputParser(pydantic_object=ScheduleEvent)
    
    # สร้าง Prompt สำหรับการประมวลผล
    prompt = PromptTemplate(
        template="""\
## คุณมีหน้าที่กรองประเภทจากคำขอผู้ใช้.

# คำขอผู้ใช้: {user_query}
## สถานที่ ท่องเที่ยวทั้งหมดที่มี เลือกจากในนี้มาตอบเท่านั้น และหากไม่มีสถานที่ตรงกับประเภทจากคำขอผู้ใช้ ให้แสดงประเภทที่ใกล้เคียง:
{unique_attr_sub_types}

# Your response should be structured as follows:
{format_instructions}
""",
        input_variables=["user_query", "unique_attr_sub_types"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    # เรียกใช้งาน PromptChain กับ LLM และ parser
    chain = prompt | llm | parser
    event = chain.invoke({"user_query": user_query, "unique_attr_sub_types": unique_attr_sub_types})
    
    # ตรวจสอบผลลัพธ์จาก LLM
    return event.get("Names", [])

# 6. Map Creation and Update
def create_map(center_lat, center_lon, zoom_start=12, user_lat=None, user_lon=None, places=None):
    """
    Create map with markers for the filtered places
    """
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
    
    # Add user's location marker
    if user_lat and user_lon:
        folium.Marker([user_lat, user_lon], popup="คุณอยู่ที่นี่", icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)
    
    
    
    # Add filtered places markers
    if places is not None:
        for _, row in places.iterrows():
            folium.Marker(
                [row['LATITUDE_LOCATION'], row['LONGITUDE_LOCATION']],
                popup=row['ATT_NAME_TH'],
                icon=folium.Icon(color="green")  # เปลี่ยนสีหมุดเป็นสีเขียว
            ).add_to(m)

    return m

# 7. Recommendation Generation
def generate_recommendation(df: pd.DataFrame, llm: ChatOpenAI) -> str:
    """
    Generates a recommendation based on filtered places.
    
    Args:
        df (pd.DataFrame): The filtered DataFrame with places.
        llm (ChatOpenAI): The LLM model used to generate the recommendation.
    
    Returns:
        str: The recommendation text.
    """
    places_info = df[['ATT_NAME_TH', 'ATT_DETAIL_TH', 'DISTANCE']].head(3)
    places_description = "\n".join([f"{index+1}. สถานที่: {row['ATT_NAME_TH']}\n   ระยะทาง: {row['DISTANCE']:.2f} กม.\n   รายละเอียด: {row['ATT_DETAIL_TH']}\n" for index, row in places_info.iterrows()])
    prompt = f"""
    ต่อไปนี้คือสถานที่ท่องเที่ยวที่กรองมาแล้วจากข้อมูลในพื้นที่ใกล้เคียง:
    {places_description}
    กรุณาให้คำแนะนำในการเลือกสถานที่ท่องเที่ยวที่เหมาะสมที่สุดจากข้อมูลที่ให้ไว้
    """
    response = llm.invoke(prompt)
    return response.content.strip()

# 8 แนะนำสถานที่ท่องเที่ยวและเปรียบเทียบสถานที่
def generate_recommendation(df: pd.DataFrame, llm) -> str:
    """
    ฟังก์ชันนี้จะใช้ LLM เพื่อให้คำแนะนำในการเลือกสถานที่ท่องเที่ยวที่เหมาะสมจากข้อมูลใน df
    """
    # รวบรวมข้อมูลที่จำเป็นจาก DataFrame
    places_info = df[['ATT_NAME_TH', 'ATT_DETAIL_TH', 'DISTANCE']].head(3)  # ใช้ 3 สถานที่แทน 5
    
    # สร้างคำอธิบายให้ LLM
    places_description = "\n".join([ 
        f"{index+1}. สถานที่: {row['ATT_NAME_TH']}\n"
        f"   ระยะทาง: {row['DISTANCE']:.2f} กม.\n"
        f"   รายละเอียด: {row['ATT_DETAIL_TH']}\n"
        for index, row in places_info.iterrows()
    ])
    
    # สร้างคำสั่งสำหรับ LLM
    prompt = f"""
    ต่อไปนี้คือสถานที่ท่องเที่ยวที่กรองมาแล้วจากข้อมูลในพื้นที่ใกล้เคียง:
    
    {places_description}
    
    กรุณาให้คำแนะนำในการเลือกสถานที่ท่องเที่ยวที่เหมาะสมที่สุดจากข้อมูลที่ให้ไว้
    """
    
    # ส่งคำสั่งไปยัง LLM
    response = llm.invoke(prompt)
    
    return response.content.strip()
