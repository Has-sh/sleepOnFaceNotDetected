import cv2
import face_recognition
import time
import os
import ctypes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use a relative path for the image
image_path = os.path.join(BASE_DIR, "your_face.jpg")

# Load and encode your face (Replace 'your_face.jpg' with an image of your face)
known_image = face_recognition.load_image_file(image_path)
known_encoding = face_recognition.face_encodings(known_image)[0]

def is_locked():
    """Check if the system is locked by detecting user activity."""
    return ctypes.windll.user32.GetForegroundWindow() == 0

def main():
    last_seen = time.time()  # Track last time your face was detected
    timeout = 10  # Seconds before sleeping

    while True:
        # Start webcam
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to RGB (for face_recognition)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces and encode them
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            found = False
            for face_encoding in face_encodings:
                # Compare with your face
                matches = face_recognition.compare_faces([known_encoding], face_encoding)
                if True in matches:
                    found = True
                    last_seen = time.time()  # Reset timer if your face is detected
                    break  # Stop checking other faces

            # If your face isn't detected for 10 seconds, lock the PC
            if not found and time.time() - last_seen > timeout:
                print(f'Your face not detected for {timeout} seconds. Locking PC...')
                ctypes.windll.user32.LockWorkStation()
                cap.release()  # Release camera before lock
                cv2.destroyAllWindows()
                break  # Exit loop to restart after unlocking

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return  # Exit the entire program

        # Wait for system to unlock
        print("System is locked. Waiting for unlock...")
        while is_locked():
            time.sleep(2)  # Check every 2 seconds

        print("System unlocked. Restarting webcam...")

if __name__ == "__main__":
    main()
