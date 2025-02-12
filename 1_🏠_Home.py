import streamlit as st
# from st_pages import Page, show_pages

# show_pages(
#     [
#         Page("app.py", "🏠 Home"),
#         Page("pages/upload.py", "📹 Upload & Analyze"),
#         # Page("pages/history.py", "📜 Workout History"),
#         Page("pages/statistics.py", "📊 Statistics"),
#         Page("pages/leaderboard.py", "🏆 Leaderboard"),
#         # Page("pages/about.py", "ℹ️ About"),
#     ]
# )
# st.set_page_config(page_title="FitSmart", page_icon="🏋️")

st.set_page_config(
    page_title="FitSmart",
    page_icon="https://raw.githubusercontent.com/darigain/fitsmart/main/visuals/favicon.png"  # Update this URL
)


# GitHub raw URL of your logo (replace with your actual repo URL)
GITHUB_USERNAME = "darigain"
REPO_NAME = "fitsmart"
LOGO_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/visuals/logo.png"

# Display the logo at the top of the page
st.image(LOGO_URL, width=250)

# # Sidebar Navigation
# st.sidebar.title("📍 Navigation")
# st.sidebar.page_link("app.py", label="🏠 Home")
# st.sidebar.page_link("pages/upload.py", label="📤 Upload & Analyze")
# # st.sidebar.page_link("pages/history.py", label="📜 Workout History")
# st.sidebar.page_link("pages/statistics.py", label="📊 Statistics")
# st.sidebar.page_link("pages/leaderboard.py", label="🏅 Leaderboard")
# # st.sidebar.page_link("pages/about.py", label="ℹ️ About")

st.markdown("""
# Welcome to **FitSmart**!  
FitSmart helps you **analyze your workout videos**, **count your reps**, and **track your progress** over time. 

*Supported exercises:*
""")
# Display GIFs as instructions
col1, col2 = st.columns(2)
with col1:
    st.image("https://media.giphy.com/media/eVCEGG1uKPPpcaDoFN/giphy.gif", caption="Squats", use_container_width=True)
with col2:
    st.image("https://media.giphy.com/media/rHGjuFX5FBRxn6AdCU/giphy.gif", caption="Push-ups", use_container_width=True)

st.markdown("""
# How to Get Started?  

👈 **Use the sidebar on the left to navigate:**  

- **📹 Upload & Analyze** – Submit your workout video and get instant analysis of your squats and push-ups.  
- **📊 Statistics** – View your exercise history, filter by date and exercise, and track your progress over time.  
- **🏆 Leaderboard** – Compete with others! Check out the **top users** and see where you rank.  

**Ready? Let’s get moving! 🎯**

# Quick Navigation 👇
""")

# Add navigation buttons inside the main page
# st.markdown("### Quick Navigation 👇")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📹 Upload Analyze"):
        st.switch_page("pages/2_📹_Upload_Analyze.py")  

with col2:
    if st.button("📊 Statistics"):
        st.switch_page("pages/3_📊_Statistics.py") 

with col3:
    if st.button("🏆 Leaderboard"):
        st.switch_page("pages/4_🏆_Leaderboard.py") 

with col4:
    if st.button("ℹ️ About"):
        st.switch_page("pages/5_ℹ️_About.py") 

# st.markdown("[📤 Upload & Analyze](pages/upload)")
# st.markdown("[📊 Statistics](pages/statistics)")
# st.markdown("[🏆 Leaderboard](pages/leaderboard)")

# st.link_button("📤 Go to Upload & Analyze", "https://fitsmart.streamlit.app/%F0%9F%93%A4%20Upload%20&%20Analyze")
# st.link_button("📊 Go to Statistics", "https://fitsmart.streamlit.app/%F0%9F%93%8A%20Statistics")
# st.link_button("🏆 Go to Leaderboard", "https://fitsmart.streamlit.app/%F0%9F%8F%86%20Leaderboard")

