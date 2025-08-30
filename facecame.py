import cv2
import numpy as np
import os
import pickle
import face_recognition
from datetime import datetime

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_detection_model = "haarcascade_frontalface_default.xml"
        
        # Create necessary directories
        os.makedirs("known_faces", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        
        # Load existing face data if available
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known faces from the database"""
        model_path = "models/face_data.pkl"
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
            print(f"Loaded {len(self.known_face_names)} known faces")
    
    def save_known_faces(self):
        """Save known faces to the database"""
        model_path = "models/face_data.pkl"
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names
        }
        with open(model_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved {len(self.known_face_names)} faces to database")
    
    def detect_faces(self, image):
        """Detect faces in an image using Haar Cascade"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + self.face_detection_model)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def register_face(self, image, name):
        """Register a new face in the system"""
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_image)
        
        if len(face_encodings) > 0:
            self.known_face_encodings.append(face_encodings[0])
            self.known_face_names.append(name)
            self.save_known_faces()
            
            # Save the image to known_faces directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"known_faces/{name}_{timestamp}.jpg"
            cv2.imwrite(filename, image)
            
            print(f"Successfully registered {name}")
            return True
        else:
            print("No face found in the image")
            return False
    
    def recognize_faces(self, image):
        """Recognize faces in an image"""
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find all faces and their encodings
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        face_names = []
        
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding
            )
            name = "Unknown"
            
            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, face_encoding
            )
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
            
            face_names.append(name)
        
        return face_locations, face_names
    
    def draw_faces(self, image, face_locations, face_names):
        """Draw bounding boxes and labels on the image"""
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Draw a box around the face
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Draw a label with a name below the face
            cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        
        return image

def main():
    # Initialize the face recognition system
    face_system = FaceRecognitionSystem()
    
    # Initialize webcam
    video_capture = cv2.VideoCapture(0)
    
    print("Face Recognition System")
    print("Press 'r' to register a new face")
    print("Press 'q' to quit")
    
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        
        if not ret:
            print("Failed to grab frame")
            break
        
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
        # Recognize faces
        face_locations, face_names = face_system.recognize_faces(small_frame)
        
        # Draw results on the frame
        frame = face_system.draw_faces(frame, face_locations, face_names)
        
        # Display the resulting frame
        cv2.imshow('Face Recognition System', frame)
        
        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Register a new face
            name = input("Enter the name of the person: ")
            ret, register_frame = video_capture.read()
            if ret:
                success = face_system.register_face(register_frame, name)
                if success:
                    print(f"Registered {name} successfully!")
                else:
                    print("Failed to register face")
    
    # Release the webcam and close windows
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()