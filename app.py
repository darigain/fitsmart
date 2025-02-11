import streamlit as st

st.set_page_config(page_title="FitSmart", page_icon="🏋️")

# Sidebar Navigation
st.sidebar.title("📍 Navigation")
st.sidebar.page_link("app.py", label="🏠 Home")
st.sidebar.page_link("pages/upload.py", label="📤 Upload & Analyze")
st.sidebar.page_link("pages/history.py", label="📜 Workout History")
st.sidebar.page_link("pages/statistics.py", label="📊 Statistics")
st.sidebar.page_link("pages/leaderboard.py", label="🏅 Leaderboard")
st.sidebar.page_link("pages/about.py", label="ℹ️ About")

st.markdown("""
## Welcome to FitSmart! 🎉
Your smart fitness assistant for tracking and improving your workouts. 
- 📹 Upload workout videos for analysis.
- 📊 Get real-time stats on your squats and push-ups.
- 🏆 Compete on the leaderboard and track your progress.
- 💡 Receive smart feedback to refine your form.
""")

st.write("👟 Ready to start? Head to the **Upload & Analyze** section!")
