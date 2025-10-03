import streamlit as st
import pandas as pd
import numpy as np

#--- Page Configuration ---
st.set_page_config(
    page_title="Indian Flight Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",)
#--- Data Loading ---
#--- using st.cache_data to avoid reloading data on every interaction
@st.cache_data
def load_data():
    """Loads the Flight Dataset from public URL."""
    url= "https://raw.githubusercontent.com/FrilantikaKusuma/Indian-Flight-Data-Analysis/refs/heads/main/airlines_flights_data.csv"
    df = pd.read_csv(url)
# drop rows with missing values for simplicity in this demo
    df.dropna(inplace=True)
    return df

df = load_data()

#---APP title and description---
st.title("✈️ Indian Airflight Dashboard Analysis")
st.markdown("""The Flights Booking Dataset of various Airlines is a scraped datewise from a famous website in a structured format. The dataset contains the records of flight travel details between the cities in India. Here, multiple features are present like Source & Destination City, Arrival & Departure Time, Duration & Price of the flight etc.""")


# --- SIDEBAR FOR FILTERS ---
st.sidebar.header("Filter Your Airlines")

# Filter for Source City
source_city = st.sidebar.multiselect(
   "Select Source City",
   options=df["source_city"].unique(),
)

# Filter for Destination
destination_city = st.sidebar.multiselect(
   "Select Destination City",
   options=df["destination_city"].unique(),
)

# Filter for sex
duration = st.sidebar.multiselect(
   "Select Duration",
   options=df["duration"].unique(),
)

# Filter for price
min_price, max_price = int(df["price"].min()), int(df["price"].max())
price_slider = st.sidebar.slider(
   "Select Price $",
   min_value=min_price,
   max_value=max_price,
   value=(min_price, max_price),
)

# --- FILTERING THE DATAFRAME ---
# Start with the full dataframe and apply filters sequentially
df_selection = df.copy()


# Apply multiselect filters only if a selection has been made for that filter
if source_city:
   df_selection = df_selection[df_selection["source_city"].isin(source_city)]
if destination_city:
   df_selection = df_selection[df_selection["destination_city"].isin(destination_city)]
if duration:
   df_selection = df_selection[df_selection["duration"].isin(duration)]

# Always apply the slider filter
df_selection = df_selection[
   (df_selection["price"] >= price_slider[0]) &
   (df_selection["price"] <= price_slider[1])
]

# Display error message if no data is selected
if df_selection.empty:
   st.warning("No data available for the selected filters. Please adjust your selection.")
   st.stop() # Halts the app execution

# --- MAIN PAGE CONTENT ---
st.subheader("📊 Key Metrics")


# --- DISPLAY KEY METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
   st.metric(label="Total Flights", value=df_selection.shape[0])
with col2:
   avg_price = round(df_selection["price"].mean(), 1)
   st.metric(label="Avg. Price (INR)", value=avg_price)
with col3:
   avg_duration = round(df_selection["duration"].mean(), 1)
   st.metric(label="Avg. Duration (Hours)", value=f"{avg_duration} hours")


st.markdown("---")


# --- VISUALIZATIONS ---
st.subheader("📈 Visualizations")


# Arrange charts in columns
viz_col1, viz_col2 = st.columns(2)


with viz_col1:
   # Scatter plot: Airlines vs. Days Left
   st.subheader("Price vs. Days Left")
   # st.scatter_chart can use a color parameter to differentiate categories
   st.line_chart(
       data=df_selection,
       x="days_left",
       y="price",
       color="#f63366"
   )


with viz_col2:
   # Bar Chart: Average Price by Airlines
   st.subheader("Average Price by Airlines")
   # Group data to calculate average body mass for the bar chart
   avg_price_by_airlines = df_selection.groupby('airline')['price'].mean().round(1)
   st.bar_chart(avg_price_by_airlines)




# --- DISPLAY RAW DATA ---
with st.expander("View Raw Data"):
   st.dataframe(df_selection)
   st.markdown(f"**Data Dimensions:** {df_selection.shape[0]} rows, {df_selection.shape[1]} columns")


st.markdown("---")
st.write("Data Source: [Airlines Flight Dataset](https://raw.githubusercontent.com/FrilantikaKusuma/Indian-Flight-Data-Analysis/refs/heads/main/airlines_flights_data.csv)")
