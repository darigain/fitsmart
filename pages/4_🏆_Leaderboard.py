import streamlit as st
import boto3
import pandas as pd
import plotly.express as px
import datetime

# AWS Credentials (Using Streamlit Secrets)
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = st.secrets["AWS_REGION"]
DYNAMODB_TABLE = st.secrets["DYNAMODB_TABLE"]

# Connect to DynamoDB
dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

table = dynamodb.Table(DYNAMODB_TABLE)

# DATA LOADING FUNCTION
@st.cache_data(show_spinner=False)
def load_data():
    """
    Connects to DynamoDB and loads data from the exercise_records table into a DataFrame.
    """
    try:
        response = table.scan()
        items = response.get("Items", [])
        
        if not items:
            return pd.DataFrame(columns=["username", "datetime", "squat_count", "pushup_count"])

        df = pd.DataFrame(items)
        df["datetime"] = pd.to_datetime(df["datetime"])  # Convert datetime to pandas format
        df["squat_count"] = df["squat_count"].astype(int)
        df["pushup_count"] = df["pushup_count"].astype(int)
        
        return df
    except Exception as e:
        st.error(f"Error retrieving data: {e}")
        return pd.DataFrame()

st.title("Leaderboard")
st.write("🏆 Champions, you are absolutely crushing it! 🌟")

# Refresh button (in the main area)
if st.button("Refresh Data"):
    load_data.clear()  # Clear the cache for load_data
    st.rerun()  # Force a rerun to load fresh data

# Load data from DynamoDB.
df = load_data()

if df.empty:
    st.warning("No data available from the database.")
    st.stop()

# ------------------------------
# EXERCISE FILTER SELECTION
# ------------------------------
exercise_filter = st.selectbox(
    "Select Exercise",
    options=["All", "Squats", "Push-ups"],
    index=0
)

# ------------------------------
# TIMEFRAME FILTER SELECTION
# ------------------------------
timeframe = st.selectbox(
    "Select Timeframe",
    options=["Last 24 hours", "Last 7 days", "Last 30 days", "All Time"],
    index=1
)

# ------------------------------
# APPLY TIMEFRAME FILTER
# ------------------------------
now = datetime.datetime.now()
if timeframe == "Last 24 hours":
    threshold = now - datetime.timedelta(hours=24)
    df = df[df["datetime"] >= threshold]
elif timeframe == "Last 7 days":
    threshold = now - datetime.timedelta(days=7)
    df = df[df["datetime"] >= threshold]
elif timeframe == "Last 30 days":
    threshold = now - datetime.timedelta(days=30)
    df = df[df["datetime"] >= threshold]
# For "All Time", no filtering is applied.

# ------------------------------
# AGGREGATE DATA BY USER
# ------------------------------
agg_df = df.groupby("username", as_index=False)[["squat_count", "pushup_count"]].sum()

# Apply exercise filter:
if exercise_filter == "Squats":
    agg_df["total_count"] = agg_df["squat_count"]
elif exercise_filter == "Push-ups":
    agg_df["total_count"] = agg_df["pushup_count"]
else:  # All
    agg_df["total_count"] = agg_df["squat_count"] + agg_df["pushup_count"]

agg_df = agg_df.sort_values(by="total_count", ascending=False)

# ------------------------------
# VISUALIZATION: TOP 10 USERS HORIZONTAL BAR CHART
# ------------------------------
top10 = agg_df.head(10)

if exercise_filter == "All":
    # Create a stacked bar chart with both metrics.
    top10_melt = top10.melt(
        id_vars="username",
        value_vars=["squat_count", "pushup_count"],
        var_name="Exercise",
        value_name="Count"
    )
    fig = px.bar(
        top10_melt,
        y="username",
        x="Count",
        color="Exercise",
        orientation="h",
        title="Top 10 Users Leaderboard (Stacked Counts)",
        labels={"username": "User", "Count": "Exercise Count"}
    )
elif exercise_filter == "Squats":
    fig = px.bar(
        top10,
        y="username",
        x="squat_count",
        orientation="h",
        title="Top 10 Users Leaderboard - Squats",
        labels={"username": "User", "squat_count": "Squat Count"}
    )
elif exercise_filter == "Push-ups":
    fig = px.bar(
        top10,
        y="username",
        x="pushup_count",
        orientation="h",
        title="Top 10 Users Leaderboard - Push-ups",
        labels={"username": "User", "pushup_count": "Push-up Count"}
    )

# Reverse the y-axis order so that the highest total is at the top.
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# TABLE: TOP 100 USERS LEADERBOARD
# ------------------------------
top100 = agg_df.head(100).copy()
top100 = top100.reset_index(drop=True)
top100["Rank"] = top100.index + 1
# Rearranging columns: Rank, username, total_count, squat_count, pushup_count.
top100 = top100[["Rank", "username", "total_count", "squat_count", "pushup_count"]]

st.subheader("Top 100 Users Leaderboard")
html_table = top100.to_html(index=False)
st.markdown(html_table, unsafe_allow_html=True)
