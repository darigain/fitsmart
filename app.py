import streamlit as st


show_pages(
    [
        Page("app.py", "🏠 Home"),
        Page("pages/upload.py", "📤 Upload & Analyze"),
        # Page("pages/history.py", "📜 Workout History"),
        Page("pages/statistics.py", "📊 Statistics"),
        Page("pages/leaderboard.py", "🏆 Leaderboard"),
        # Page("pages/about.py", "ℹ️ About"),
    ]
)
st.set_page_config(page_title="FitSmart", page_icon="🏋️")

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
## Welcome to FitSmart! 🎉
Your smart fitness assistant for tracking and improving your workouts. 
- 📹 Upload workout videos for analysis.
- 📊 Get real-time stats on your squats and push-ups.
- 🏆 Compete on the leaderboard and track your progress.
- 💡 Receive smart feedback to refine your form.
""")

st.write("👟 Ready to start? Head to the **Upload & Analyze** section!")
