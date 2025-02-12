import streamlit as st

st.title("ℹ️ About FitSmart")

## 💫 Goal
st.header("💫 Goal")
st.markdown(
    """
    My passion is making **simple and accessible fitness** a daily habit.  
    I truly believe that regular exercise boosts **health and well-being**. 
    But let’s be honest—**staying motivated** is hard.  
    
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
    - 🏋️‍♂️ **Get instant analysis** – rep count and feedback (coming soon).
    - 📊 **Track progress** with workout history and statistics.
    - 🏆 **Compete on the leaderboard** and challenge friends.
    """
)

## ⚙️ Methodology
st.header("⚙️ Methodology")
st.markdown(
    """
**How does FitSmart work?**  
- Uses the **MediaPipe** computer vision library (by Google) to detect squats and push-ups.  
- Tracks **key body positions** and calculates **angles** to count reps automatically.  
- Saves workout data in a **cloud database** for tracking progress.  
- Future improvements will include **form analysis, smart insights, and AI-driven recommendations**.

🔬 **Next Steps:**  
- Adding **personalized feedback** to improve exercise form.  
- Detecting **common mistakes** and suggesting corrections.  
- Making workouts **even more fun and effective!**  
    """
)

st.info("👈 Use the sidebar to explore FitSmart's features!")
