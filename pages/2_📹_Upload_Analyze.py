import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import subprocess
import datetime
import boto3

# Load AWS credentials from Streamlit secrets
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
    hip_angle = calculate_angle(knee, hip, shoulder)
    elbow_angle = calculate_angle(shoulder, wrist, hip)
    stand_angle = calculate_angle(shoulder, ankle, [ankle[0], ankle[1] - 1])
    plank_angle = calculate_angle(shoulder, hip, ankle)

    if stand_angle < 40:
        return "squat"
    if torso_angle > 45 and hip_angle > 100:
        return "push-up"
    return "unknown"

# Function to count reps
def count_reps(current_phase, prev_phase, count):
    if prev_phase == "down" and current_phase == "up":
        return count + 1, current_phase
    return count, current_phase

# Ensure the video is in vertical orientation by rotating frames if needed.
def fix_video_orientation(frame, recorded_on_android=False):
    height, width = frame.shape[:2]
    if width > height:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    if recorded_on_android:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    return frame

# Re-encode the video with FFmpeg
def reencode_video(input_path, output_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path, "-vcodec", "libx264", "-crf", "28", output_path
    ])

# Streamlit UI
st.title("📹 Upload & Analyze")

st.info("Example screenshots of exercises being performed:")

image_urls = [
    "https://raw.githubusercontent.com/darigain/fitsmart/main/visuals/squat_down.png",  # Replace with actual image path or URL
    "https://raw.githubusercontent.com/darigain/fitsmart/main/visuals/squat_up.png",
    "https://raw.githubusercontent.com/darigain/fitsmart/main/visuals/pushup_down.png",
    "https://raw.githubusercontent.com/darigain/fitsmart/main/visuals/pushup_up.png"
]

with st.expander("👉Click to view images👈", expanded=False):
    # Create two main columns for the 2x2 layout
    col1, col2 = st.columns(2)
    
    # Display images in the first row
    with col1:
        st.image(image_urls[0], use_container_width=True)  # First image in the first column
    with col2:
        st.image(image_urls[1], use_container_width=True)  # Second image in the second column
    
    # Create another two columns for the second row
    col3, col4 = st.columns(2)
    
    # Display images in the second row
    with col3:
        st.image(image_urls[2], use_container_width=True)  # Third image in the first column
    with col4:
        st.image(image_urls[3], use_container_width=True)  # Fourth image in the second column

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
recorded_on_android = st.checkbox("Recorded using an Android front camera? (If video is upside down)")

# Upload video
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

if username and uploaded_file:
    # Save file temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.write(uploaded_file.read())
    video_path = temp_file.name

    cap = cv2.VideoCapture(video_path)

    # Progress bar in Streamlit
    progress_bar = st.progress(0)

    squat_count, pushup_count = 0, 0
    squat_phase, pushup_phase = "up", "up"
    frame_count, frame_skip = 0, 3
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
            
            frame = fix_video_orientation(frame, recorded_on_android)
            
            # Resize frame for performance
            frame = cv2.resize(frame, (240, 426)) # (480, 640)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

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

                exercise = detect_exercise_type(keypoints)

                if exercise == "squat":
                    knee_angle = calculate_angle(keypoints["RIGHT_HIP"], keypoints["RIGHT_KNEE"], keypoints["RIGHT_ANKLE"])
                    hip_angle = calculate_angle(keypoints["RIGHT_KNEE"], keypoints["RIGHT_HIP"], keypoints["RIGHT_SHOULDER"])
                    current_phase = "down" if (knee_angle < 90) & (hip_angle < 100) else "up"
                    squat_count, squat_phase = count_reps(current_phase, squat_phase, squat_count)

                elif exercise == "push-up":
                    elbow_angle = calculate_angle(keypoints["RIGHT_SHOULDER"], keypoints["RIGHT_ELBOW"], keypoints["RIGHT_WRIST"])
                    knee_shoulder_angle = calculate_angle(keypoints["RIGHT_SHOULDER"], keypoints["RIGHT_KNEE"], 
                                                  [keypoints["RIGHT_KNEE"][0], keypoints["RIGHT_KNEE"][1] - 1])
                    current_phase = "down" if (elbow_angle < 100) & (knee_shoulder_angle > 65) else "up"
                    pushup_count, pushup_phase = count_reps(current_phase, pushup_phase, pushup_count)

                # Draw exercise type and counts on the frame
                cv2.putText(image, f"Exercise: {exercise}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f"Squats: {squat_count} ({squat_phase})", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(image, f"Push-Ups: {pushup_count} ({pushup_phase})", (50, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
            
            progress_value = min(1.0, max(0.0, frame_count / max(1, total_frames)))
            progress_bar.progress(progress_value)
            processed_frames.append(image)

    cap.release()

    st.success("Processing Complete!")
    st.write(f"**🏋️ Total Squats:** {squat_count}")
    st.write(f"**💪 Total Push-Ups:** {pushup_count}")

    # ✅ Insert into DynamoDB
    current_time = datetime.datetime.now() #.isoformat()
    try:
        table.put_item(
            Item={
                "username": username,
                "datetime": current_time,
                "squat_count": squat_count,
                "pushup_count": pushup_count
            }
        )
        st.success("Record inserted into DynamoDB successfully!")
    except Exception as e:
        st.error(f"Error inserting record into DynamoDB: {e}")

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
