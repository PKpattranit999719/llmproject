import pandas as pd
from geopy.distance import geodesic
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain.agents import Tool
import folium
import ipywidgets as widgets
from IPython.display import display

# ======================== CONFIGURATION ========================

def configure_llm(url: str, api_key: str, model: str = 'gpt-4o-mini', max_tokens: int = 1000):  
    """
    Configure the LLM connection.
    """
    return ChatOpenAI(model=model, base_url=url, api_key=api_key, max_tokens=max_tokens)

# ======================== DATA HANDLING ========================

def load_data(filepath: str) -> pd.DataFrame:
    """
    Load CSV data into a DataFrame.
    """
    return pd.read_csv(filepath)

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the data by removing rows with missing latitude or longitude.
    """
    return df.dropna(subset=['LATITUDE_LOCATION', 'LONGITUDE_LOCATION'])

def calculate_distance(user_location, place_location):
    """
    Calculate the distance between two locations.
    """
    return geodesic(user_location, place_location).kilometers

# เพิ่มเรื่อง ARG บรรยายเพิ่มแต่ละตัว
def filter_data( 
    df: pd.DataFrame,
    thai_name: str = None,
    region: str = None,
    subdistrict: str = None,
    district: str = None,
    province: str = None,
    category: str = None,
    subtype: str = None,
    user_location: tuple = None,
    radius: float = None
) -> pd.DataFrame:
    """
    Filter the data based on the specified criteria.
    """
    if df.empty:
        return pd.DataFrame()

    if thai_name:
        df = df[df['ATT_NAME_TH'].str.contains(thai_name, na=False, case=False)]
    if region:
        df = df[df['REGION_NAME_TH'].str.contains(region, na=False, case=False)]
    if subdistrict:
        df = df[df['SUBDISTRICT_NAME_TH'].str.contains(subdistrict, na=False, case=False)]
    if district:
        df = df[df['DISTRICT_NAME_TH'].str.contains(district, na=False, case=False)]
    if province:
        df = df[df['PROVINCE_NAME_TH'].str.contains(province, na=False, case=False)]
    if category:
        df = df[df['ATTR_CATAGORY_TH'].str.contains(category, na=False, case=False)]
    if subtype:
        df = df[df['ATTR_SUB_TYPE_TH'].str.contains(subtype, na=False, case=False)]

    if user_location and radius:
        df['DISTANCE'] = df.apply(
            lambda row: calculate_distance(user_location, (row['LATITUDE_LOCATION'], row['LONGITUDE_LOCATION'])), axis=1
        )
        df = df[df['DISTANCE'] <= radius]

    return df

# ======================== LLM INTERACTION ========================

def extract_keywords_from_query(llm, query: str) -> str:
    """
    Extract keywords from the user query using LLM.
    """
    response = llm.invoke(f"แยกคำสำคัญจากคำถามนี้: '{query}' และแสดงคำสำคัญที่เกี่ยวข้องที่สามารถใช้กรองข้อมูลได้")
    return response.content.strip()

# ======================== AGENT CREATION ========================

def create_agent(llm, df: pd.DataFrame):
    """
    Create a Pandas DataFrame agent with LLM and custom tools.
    """
    filter_data_tool = Tool(
        name="Filter Data",
        func=filter_data,
        description="กรองข้อมูลจาก DataFrame ตามคอลัมน์ต่างๆ รวมถึงการกรองระยะทาง"
    )

    return create_pandas_dataframe_agent(
        llm=llm,
        df=df,
        verbose=True,
        allow_dangerous_code=True,
        agent_type="tool-calling",
    )

# ======================== MAP VISUALIZATION ========================

def create_map(center_lat, center_lon, zoom_start=12, user_lat=None, user_lon=None):
    """
    Create a map centered at the specified latitude and longitude.
    """
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)

    if user_lat and user_lon:
        folium.Marker([user_lat, user_lon], popup="คุณอยู่ที่นี่", icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)

    return m

def update_map(filtered_data, dropdown_value, user_location):
    """
    Update the map based on the selected place from the dropdown.
    """
    selected_place = filtered_data[filtered_data['ATT_NAME_TH'] == dropdown_value].iloc[0]
    lat, lon = selected_place['LATITUDE_LOCATION'], selected_place['LONGITUDE_LOCATION']

    m = create_map(lat, lon, user_lat=user_location[0], user_lon=user_location[1])
    
    for _, row in filtered_data.iterrows():
        folium.Marker([row['LATITUDE_LOCATION'], row['LONGITUDE_LOCATION']],
                      popup=row['ATT_NAME_TH'],
                      icon=folium.Icon(color="green")).add_to(m)
    
    display(m)

# ======================== MAIN PROCESS ========================

def main():
    # Load and preprocess data
    filepath = "splitData.csv"
    df = load_data(filepath)
    df = preprocess_data(df)

    # Configure LLM
    url = "<your_url>"
    api_key = "<your_api_key>"
    llm = configure_llm(url, api_key)

    # Extract keywords and filter data
    user_query = "ช่วยหาแหล่งท่องเที่ยวทางธรรมชาติในจังหวัดนครปฐมให้หน่อย"
    keywords = extract_keywords_from_query(llm, user_query)
    print("Keywords:", keywords)

    filtered_data = filter_data(df, province="นครปฐม", category="ธรรมชาติ", user_location=(14.022788, 99.978337), radius=50)
    print("Filtered Data:")
    print(filtered_data)

    # Visualize map
    dropdown = widgets.Dropdown(
        options=filtered_data['ATT_NAME_TH'].tolist(),
        description='สถานที่:',
        value=filtered_data['ATT_NAME_TH'].iloc[0]
    )

    dropdown.observe(lambda change: update_map(filtered_data, change.new, (14.022788, 99.978337)), names='value')
    display(widgets.VBox([dropdown]))

    initial_place = filtered_data.iloc[0]
    m = create_map(initial_place['LATITUDE_LOCATION'], initial_place['LONGITUDE_LOCATION'], user_lat=14.022788, user_lon=99.978337)

    for _, row in filtered_data.iterrows():
        folium.Marker([row['LATITUDE_LOCATION'], row['LONGITUDE_LOCATION']],
                      popup=row['ATT_NAME_TH'],
                      icon=folium.Icon(color="green")).add_to(m)

    display(m)

if __name__ == "__main__":
    main()
