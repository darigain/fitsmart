import streamlit as st

st.title("ℹ️ About FitSmart")

## 💫 Goal
st.header("💫 Goal")
st.markdown(
    """
    My passion is making **simple and accessible fitness** a daily habit.  
    I truly believe that **regular exercise improves health and well-being**, and it’s **empowering to work out anywhere**, without the need for gym memberships.

    But let’s be honest—**staying motivated is hard**.  
    What helps?  

    ✅ A **record** of your workouts: a journal entry, a message to a friend, or **a smart tool like FitSmart**.  

    **FitSmart** helps you stay on track, build consistency, and make fitness a part of your lifestyle.
    """
)

## 📱 App Overview
st.header("📱 App Overview")
st.markdown(
    """
    FitSmart transforms your **phone into a smart fitness tracker**:

    - 📹 **Record** a quick workout video of squats and push-ups.
    - 🏋️‍♂️ **Get instant analysis** – rep count & feedback (coming soon).
    - 📊 **Track progress** with workout history and statistics.
    - 🏆 **Compete on the leaderboard** and challenge friends.

    🚀 **No excuses—just move!**
    """
)

## ⚙️ Methodology
st.header("⚙️ Methodology")
st.markdown(
    """
    **How does FitSmart work?**  
    - Uses **computer vision** to detect squats and push-ups.  
    - Tracks **key body positions** to count reps automatically.  
    - Saves workout data in a **secure database** for tracking progress.  
    - Future improvements will add **form analysis, smart insights, and AI-driven recommendations**.

    🔬 **Next Steps:**  
    - Adding **personalized feedback** to improve exercise form.  
    - Detecting **common mistakes** and suggesting corrections.  
    - Making workouts **even more fun and effective!**
    """
)

st.info("👈 Use the sidebar to explore FitSmart's features!")
