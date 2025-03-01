import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import boto3

# Load credentials from Streamlit secrets
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = st.secrets["AWS_REGION"]
DYNAMODB_TABLE = st.secrets["DYNAMODB_TABLE"]

# Initialize DynamoDB client
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
table = dynamodb.Table(DYNAMODB_TABLE)

# DATA LOADING FUNCTION (from DynamoDB)
@st.cache_data(show_spinner=False)
def load_data():
    """
    Connect to DynamoDB and load exercise_records data into a DataFrame.
    """
    try:
        response = table.scan()  # Fetch all records from DynamoDB
        items = response.get("Items", [])
        if not items:
            return pd.DataFrame()  # Return an empty DataFrame if no records exist

        df = pd.DataFrame(items)
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])  # Ensure datetime format
        return df

    except Exception as e:
        st.error(f"Error retrieving data from DynamoDB: {e}")
        return pd.DataFrame()

st.title("Exercise Statistics")
st.write("Are you a push-up or squat hero? 🏋️‍♀️💪 Check it out! 🔍")

# ------------------------------
# Refresh Button
# ------------------------------
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()  # Force a rerun to load fresh data

# Load the full data from DynamoDB
data_full = load_data()

if data_full.empty:
    st.warning("No data found in the database.")
    st.stop()

# Sidebar widget for filtering by user
user_options = sorted(data_full['username'].unique().tolist())
selected_user = st.selectbox("Select a user", ["All Users"] + user_options)

# Filter the data based on the selected user.
if selected_user != "All Users":
    df_filtered = data_full[data_full['username'] == selected_user].copy()
else:
    df_filtered = data_full.copy()

# Sidebar widget for aggregation frequency.
frequency = st.selectbox("Select aggregation frequency", ["Daily", "Weekly", "Monthly"])

# Prepare data for plotting based on the selected frequency.
df_chart = df_filtered.copy()  # Work on a copy so as not to alter the original filtered data.

if frequency == "Daily":
    df_chart['date'] = df_chart['datetime'].dt.date
    df_grouped = (
        df_chart.groupby("date")[["squat_count", "pushup_count"]]
                .sum()
                .reset_index()
    )
    df_grouped['date'] = pd.to_datetime(df_grouped['date'])
elif frequency == "Weekly":
    df_chart['week'] = df_chart['datetime'].dt.to_period('W').apply(lambda r: r.start_time)
    df_grouped = (
        df_chart.groupby("week")[["squat_count", "pushup_count"]]
                .sum()
                .reset_index()
                .rename(columns={'week': 'date'})
    )
elif frequency == "Monthly":
    df_chart['month'] = df_chart['datetime'].dt.to_period('M').apply(lambda r: r.start_time)
    df_grouped = (
        df_chart.groupby("month")[["squat_count", "pushup_count"]]
                .sum()
                .reset_index()
                .rename(columns={'month': 'date'})
    )
else:
    df_grouped = df_chart.copy()

# Create an interactive line plot with two lines (one for squat_count, one for pushup_count).
fig = px.line(
    df_grouped,
    x="date",
    y=["squat_count", "pushup_count"],
    markers=True,
    labels={"value": "Count", "date": "Date", "variable": "Exercise"},
    title=f"Exercise Counts ({frequency} Aggregation)"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------------------
# NEW FEATURE: HTML Table "Recent User's Data"
# --------------------------------------------------------------------------
st.subheader("Recent User's Data")
# Sort the filtered data by datetime in descending order.
df_recent = df_filtered.sort_values(by="datetime", ascending=False)
# Convert the DataFrame to an HTML table without the default index.
html_table = df_recent.to_html(index=False, classes="table table-striped")
st.markdown(html_table, unsafe_allow_html=True)
