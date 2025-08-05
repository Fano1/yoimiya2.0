import cv2
import mediapipe as mp

# Initialize mediapipe solutions
mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_selfie_segmentation = mp.solutions.selfie_segmentation
mp_objectron = mp.solutions.objectron
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def run_detection(choice):
    cap = cv2.VideoCapture(0)
    
    if choice == '1':  # Face Detection
        with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as detector:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = detector.process(frame_rgb)
                if results.detections:
                    for detection in results.detections:
                        mp_drawing.draw_detection(frame, detection)
                cv2.imshow("Face Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    
    elif choice == '2':  # Face Mesh
        with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as mesh:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = mesh.process(frame_rgb)
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            face_landmarks,
                            mp_face_mesh.FACEMESH_TESSELATION,
                            mp_drawing_styles.get_default_face_mesh_tesselation_style(),
                            mp_drawing_styles.get_default_face_mesh_contours_style()
                        )
                cv2.imshow("Face Mesh", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    elif choice == '3':  # Hand Tracking
        with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style()
                        )
                cv2.imshow("Hand Tracking", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    elif choice == '4':  # Pose Estimation
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(frame_rgb)
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                cv2.imshow("Pose Estimation", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    elif choice == '5':  # Selfie Segmentation
        with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as segmenter:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = segmenter.process(frame_rgb)

                condition = results.segmentation_mask > 0.1
                bg_image = cv2.GaussianBlur(frame, (55, 55), 0)
                output_frame = cv2.where(condition[..., None], frame, bg_image)

                cv2.imshow("Selfie Segmentation (Background Blur)", output_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    elif choice == '6':  # Objectron (3D Object Detection) - Box detection
        with mp_objectron.Objectron(static_image_mode=False,
                                   max_num_objects=5,
                                   min_detection_confidence=0.5,
                                   min_tracking_confidence=0.5,
                                   model_name='Cup') as objectron:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = objectron.process(frame_rgb)
                if results.detected_objects:
                    for detected_object in results.detected_objects:
                        mp_drawing.draw_landmarks(
                            frame,
                            detected_object.landmarks_2d,
                            mp_objectron.BOX_CONNECTIONS)
                        mp_drawing.draw_axis(frame, detected_object.rotation,
                                             detected_object.translation)
                cv2.imshow("Objectron - Cup Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    else:
        print("Invalid choice")

    cap.release()
    cv2.destroyAllWindows()

def main():
    print("""
    Select MediaPipe feature to run:
    1 - Face Detection
    2 - Face Mesh
    3 - Hand Tracking
    4 - Pose Estimation
    5 - Selfie Segmentation (Background Blur)
    6 - Objectron (3D Object Detection - Cup)
    q - Quit
    """)

    while True:
        choice = input("Enter your choice: ").strip()
        if choice == 'q':
            print("Exiting... Stay")
            break
        run_detection(choice)

if __name__ == "__main__":
    main()
