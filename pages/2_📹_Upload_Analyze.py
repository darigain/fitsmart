import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import subprocess
import psycopg2 
import datetime  

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Function to calculate angle
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# Function to detect exercise type
def detect_exercise_type(keypoints):
    shoulder = keypoints["RIGHT_SHOULDER"]
    hip = keypoints["RIGHT_HIP"]
    knee = keypoints["RIGHT_KNEE"]
    wrist = keypoints["RIGHT_WRIST"]
    ankle = keypoints["RIGHT_ANKLE"]

    torso_angle = calculate_angle(shoulder, hip, [hip[0], hip[1] - 1])
    knee_angle = calculate_angle(hip, knee, ankle)
    elbow_angle = calculate_angle(shoulder, wrist, hip)
    stand_angle = calculate_angle(shoulder, ankle, [ankle[0], ankle[1] - 1])
    plank_angle = calculate_angle(shoulder, hip, ankle)

    if stand_angle < 40:
        return "squat"
    if plank_angle > 150 and knee_angle > 150:
        return "push-up"
    return "unknown"

# Function to count reps
def count_reps(current_phase, prev_phase, count):
    if prev_phase == "down" and current_phase == "up":
        return count + 1, current_phase
    return count, current_phase

# Ensure the video is in vertical orientation by rotating frames if needed.
def fix_video_orientation(frame):
    height, width = frame.shape[:2]
    if width > height:  # Landscape orientation detected
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)  # COUNTERCLOCKWISE
    return frame

# Streamlit UI
st.title("📹 Upload & Analyze")

# # Display GIFs as instructions
# col1, col2 = st.columns(2)
# with col1:
#     st.image("https://media.giphy.com/media/eVCEGG1uKPPpcaDoFN/giphy.gif", caption="Squats", use_container_width=True)
# with col2:
#     st.image("https://media.giphy.com/media/rHGjuFX5FBRxn6AdCU/giphy.gif", caption="Push-ups", use_container_width=True)

image_urls = [
    "https://raw.githubusercontent.com/darigain/fitsmart/main/visuals/squat_down.png",  # Replace with actual image path or URL
    "https://raw.githubusercontent.com/darigain/fitsmart/main/visuals/squat_up.png",
    "https://raw.githubusercontent.com/darigain/fitsmart/main/visuals/pushup_down.png",
    "https://raw.githubusercontent.com/darigain/fitsmart/main/visuals/pushup_up.png"
]

# Create four columns for layout
col1, col2, col3, col4 = st.columns(4)

# Display images in respective columns
with col1:
    st.image(image_urls[0], use_container_width=True)
with col2:
    st.image(image_urls[1], use_container_width=True)
with col3:
    st.image(image_urls[2], use_container_width=True)
with col4:
    st.image(image_urls[3], use_container_width=True)

st.markdown("""
💡 **The easiest way to start:**  

1️⃣ Open **FitSmart** in your phone browser  
2️⃣ Enter your **username**  
3️⃣ Record a quick video of **squats** and **push-ups**. Film the side of the body, using vertical orientation (frontal/back camera).  
4️⃣ Get **instant analysis**  

⚠️ **Note:** Your video **is not stored**! Download it if you want to save it.  
""")
    
# Username input
username = st.text_input("Enter your username:")

# Upload video
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

if username and uploaded_file:
    # Save file temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.write(uploaded_file.read())
    video_path = temp_file.name

    # Load video
    cap = cv2.VideoCapture(video_path)

    # Progress bar in Streamlit
    progress_bar = st.progress(0)

    # Initialize counters
    squat_count, pushup_count = 0, 0
    squat_phase, pushup_phase = "up", "up"
    frame_count, frame_skip = 0, 3

    # Store processed frames
    processed_frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Skip frames for performance
            if frame_count % frame_skip != 0:
                frame_count += 1
                continue
            frame_count += 1
            
            # Fix orientation if needed
            frame = fix_video_orientation(frame)
            
            # Resize frame
            # frame = cv2.resize(frame, (480, 640))
            frame = cv2.resize(frame, (240, 426))

            # Convert for Mediapipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Extract keypoints
                landmarks = results.pose_landmarks.landmark
                keypoints = {
                    "RIGHT_SHOULDER": [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                       landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
                    "RIGHT_HIP": [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y],
                    "RIGHT_KNEE": [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y],
                    "RIGHT_WRIST": [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y],
                    "RIGHT_ANKLE": [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y],
                    "RIGHT_ELBOW": [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                }

                # Detect exercise (unchanged)
                exercise = detect_exercise_type(keypoints)

                # Count reps (unchanged)
                if exercise == "squat":
                    knee_angle = calculate_angle(keypoints["RIGHT_HIP"], keypoints["RIGHT_KNEE"], keypoints["RIGHT_ANKLE"])
                    hip_angle = calculate_angle(keypoints["RIGHT_KNEE"], keypoints["RIGHT_HIP"], keypoints["RIGHT_SHOULDER"])
                    current_phase = "down" if (knee_angle < 90) & (hip_angle < 100) else "up"
                    squat_count, squat_phase = count_reps(current_phase, squat_phase, squat_count)

                elif exercise == "push-up":
                    elbow_angle = calculate_angle(keypoints["RIGHT_SHOULDER"], keypoints["RIGHT_ELBOW"], keypoints["RIGHT_WRIST"])
                    stand_angle = calculate_angle(keypoints["RIGHT_SHOULDER"], keypoints["RIGHT_ANKLE"], 
                                                  [keypoints["RIGHT_ANKLE"][0], keypoints["RIGHT_ANKLE"][1] - 1])
                    current_phase = "down" if (elbow_angle < 90) & (stand_angle > 75) else "up"
                    pushup_count, pushup_phase = count_reps(current_phase, pushup_phase, pushup_count)
                
                # Draw exercise type and counts on the frame
                cv2.putText(image, f"Exercise: {exercise}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f"Squats: {squat_count} ({squat_phase})", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(image, f"Push-Ups: {pushup_count} ({pushup_phase})", (50, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)

            progress_value = min(1.0, max(0.0, frame_count / max(1, total_frames)))  # Prevents division by zero
            progress_bar.progress(progress_value)
            # Update progress bar
            # progress_bar.progress(frame_count / total_frames)

            # Store processed frames
            processed_frames.append(image)

    cap.release()

    # Display results
    st.success("Processing Complete!")
    st.write(f"**🏋️ Total Squats:** {squat_count}")
    st.write(f"**💪 Total Push-Ups:** {pushup_count}")

    # NEW FEATURE: Insert record into the database table (username, datetime, squat_count, pushup_count)
    if username:  # Only insert if username is provided
        try:
            # Connect to the database using credentials from Streamlit secrets
            conn = psycopg2.connect(
                host=st.secrets["db"]["host"],
                database=st.secrets["db"]["database"],
                user=st.secrets["db"]["user"],
                password=st.secrets["db"]["password"],
                port=st.secrets["db"]["port"]
            )
            cursor = conn.cursor()
            
            # Insert record into the table 'exercise_records'
            insert_query = """
            INSERT INTO exercise_records (username, datetime, squat_count, pushup_count)
            VALUES (%s, %s, %s, %s)
            """
            current_time = datetime.datetime.now()
            cursor.execute(insert_query, (username, current_time, squat_count, pushup_count))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Record inserted into database successfully!")
        except Exception as e:
            st.error(f"Error inserting record into database: {e}")
    else:
        st.warning("Username not provided. Record not saved to database.")

    # Re-encode the video with FFmpeg
    def reencode_video(input_path, output_path):
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, "-vcodec", "libx264", "-crf", "28", output_path
        ])

    # Save the video and re-encode it
    temp_output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    final_video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

    # Save the video using OpenCV
    height, width, _ = processed_frames[0].shape
    out = cv2.VideoWriter(temp_output_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width, height))
    for frame in processed_frames:
        out.write(frame)
    out.release()

    # Re-encode with FFmpeg
    reencode_video(temp_output_path, final_video_path)

    # Display the re-encoded video
    st.video(final_video_path)
    st.info("👈 Use the sidebar to find your last submission on the 📊 Statistics page, or check your position on the 🏆 Leaderboard page!")
