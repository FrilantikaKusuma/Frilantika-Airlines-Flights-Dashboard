import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#--- Configuration and Setup
st.set_page_config(
   page_title="Airline Flight Data Analysis Dashboard",
   page_icon="✈️",
   layout="wide",
   initial_sidebar_state="expanded",
)

#---Loading Data---
@st.cache_data
def load_data():
   """Loads the Flight Dataset from public URL."""
   url= "https://raw.githubusercontent.com/FrilantikaKusuma/Indian-Flight-Data-Analysis/refs/heads/main/airlines_flights_data.csv"
   df = pd.read_csv(url)

   # Drop unnecessary 'index' and 'flight' columns for analysis
   df.drop(columns=['index', 'flight'], errors='ignore')

   # Standardize column names (days_left to 'days left)
   df.columns = df.columns.str.replace('_', ' ').str.title()

   # Convert relevant columns to numeric and drop rows with errors
   for col in ['price', 'duration', 'days left']:
      if col in df.columns:
         df[col] = pd.to_numeric(df[col], errors='coerce')
   
   return df.dropna()

df = load_data()

# Title and Header
st.title("✈️ Indian Flight Price Analysis Dashboard")
st.markdown("""The Flights Booking Dataset of various Airlines is a scraped datewise from a famous website in a structured format. The dataset contains the records of flight travel details between the cities in India. Here, multiple features are present like Source & Destination City, Arrival & Departure Time, Duration & Price of the flight etc.""")

#---Sidebar Filter---
st.sidebar.header("Filter Options")

# Helper function to create multiselect filter
def create_filter(df, column_name):
   options = sorted(df[column_name].unique())
   selected = st.sidebar.multiselect(
      f"Select {column_name}",
      options=options,
      default=options
   )
   return selected

# Apply Filters
selected_airlines = create_filter(df, 'Airline')
selected_source_cities = create_filter(df, 'Source City')
selected_dest_cities = create_filter(df, 'Destination City')
selected_classes = create_filter(df, 'Class')
selected_stops = create_filter(df, 'Stops')

# Apply all filters
df_filtered = df[
   df['Airline'].isin(selected_airlines) &
   df['Source City'].isin(selected_source_cities) &
   df['Destination City'].isin(selected_dest_cities) &
   df['Class'].isin(selected_classes) &
   df['Stops'].isin(selected_stops)
]

# Display filter count
st.sidebar.metric(
   "Total Flights Selected",
   f"{len(df_filtered):,}",
   delta=f"{len(df):,} Total in Dataset",
   delta_color="off"
)

# Handle empty filtered data
if df_filtered.empty:
   st.warning("No data matches the selected filters. Please adjust your selections.")
   st.stop()

#--- Main Dasboard Content---

# 1. Key Performance Indicators (KPIs)
st.header("Key Flight Metrics")
col1, col2, col3, col4 = st.columns(4)

avg_price = df_filtered['Price'].mean()
avg_duration = df_filtered['Duration'].mean()
unique_flights = len(df_filtered)
price_range = df_filtered['Price'].max() - df_filtered['Price'].min()

col1.metric("Average Price (INR)", f"₹ {avg_price:,.2f}")
col2.metric("Average Duration (Hours)", f"{avg_duration:.2f} hrs")
col3.metric("Total Flight Samples", f"{unique_flights:,}")
col4.metric("Price (Max - Min)", f"₹ {price_range:,.0f}")

# 2 Visualization Row 1: Price Distribution & Airline Performance
st.markdown("""_____""")
st.header("Price Distribution and Carrier Performance")
col_vis_1, col_vis_2 = st.columns(2)

with col_vis_1:
   st.subheader("Price Distribution by Class")

   # Histogram of Price Distribution
   fig_hist = px.histogram(
      df_filtered,
      x="Price",
      color="Class",
      marginal="box",
      title="Price Frequency and Box Plot by Tracel Class",
      hover_data=df_filtered.columns,
      color_discrete_map={
         'Economy': '#4C78A8',
         'Business': '#F58518'
      }
   )
   fig_hist.update_layout(
    xaxis_title="Price (INR)",
    yaxis_title="Count of Flights",
    legend_title="Class"
   )
   st.plotly_chart(fig_hist, user_container_width=True)

with col_vis_2 :
   st.subheader("Average Price by Airline")

   #Bar Chart for Average Price per Airline
   airline_avg_price = df_filtered.groupby('Airline')['Price'].mean().reset_index()
   airline_avg_price = airline_avg_price.sort_values(by='Price', ascending=False)

   fig_bar = px.bar(
      airline_avg_price,
      x="Airline",
      y="Price",
      title="Mean Price Across Different Airlines",
      color="Airline",
      template="plotly_white"
   )

   fig_bar.update_layout(
      xaxis_title="Airline",
      yaxis_title="Average Price (INR)",
      showlegend=False
   )
   st.plotly_chart(fig_bar, use_container_width=True)

# 3. Visualization Row 2: Price vs Booking Time & Duration
st.markdown("""----""")
st.header("Booking Dynamics and Flight Characteristics")
col_vis_3, col_vis_4 = st.columns(2)

with col_vis_3:
   st.subheader("Price vs. Days Left Before Departure")
   # Line chart showing average price trend as departue nears
   price_vs_days = df_filtered.groupby('Days Left')['Price'].mean().reset_index()

   fig_line = px.line(
      price_vs_days,
      x='Days Left',
      y='Price',
      title='Average Price Trend as Departure Day Approaches',
      markers=True,
      line_shape='spline'
   )

   fig_line.update_traces(line=dict(color='#E45756', width=3))
   fig_line.update_layout(
      xaxis_title="Days Left Until Departure Time (Closer to 0 is closer to travel date)",
      yaxis_title="Average Price (INR)"
   )
   # Highlight the general trend of price increase as days left decreases
   st.plotly_chart(fig_line, use_container_width=True)

with col_vis_4:
   st.subheader("Duration vs, Price by Number of Stops")
   # Scatter Plot to show relationship between duration and price
   fig_scatter = px.scatter(
      df_filtered,
      x="Duration",
      y="Price",
      color="Stops",
      hover_data=['Airline', 'Source City', 'Destination City', 'Departure Time'],
      title="Price vs. Duration, Colored by Number of Stops",
      color_discrete_sequence=px.colors.qualitative.Bold
   )
   fig_scatter.update_layout(
      xaxis_title="Flight Duration (Hours)",
      yaxis_title="Price (INR)"
   )
   st.plotly_chart(fig_scatter, use_container_width=True)

# 4. Row Data View (Optional but helpful)
st.markdown("""This analyse will be helpful for those working in Airlines, Travel domain.""")
st.subheader("Row Filtered Data Sample")
st.dataframe(df_filtered.head(100))

# --- Footer ---
st.markdown("""
<style>
.stApp {
    background-color: #f0f2f6;
}
.st-emotion-cache-18ni7ap {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)
