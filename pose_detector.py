import cv2
import mediapipe as mp

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.landmarks = None

        # Har finger ke liye alag color
        self.finger_colors = {
            'thumb':  (0, 215, 255),   # Gold
            'index':  (0, 255, 100),   # Green
            'middle': (255, 100, 0),   # Blue
            'ring':   (255, 0, 200),   # Purple
            'pinky':  (0, 100, 255),   # Orange
            'palm':   (200, 200, 200)  # White/grey
        }

        # Face mesh drawing spec — cyan dots
        self.face_dot_spec = self.mp_draw.DrawingSpec(
            color=(0, 255, 255), thickness=1, circle_radius=1
        )
        self.face_line_spec = self.mp_draw.DrawingSpec(
            color=(0, 180, 180), thickness=1
        )

    def draw_fingers(self, frame, hand_landmarks):
        h, w = frame[:2] if isinstance(frame, tuple) else frame.shape[:2]

        def pt(idx):
            lm = hand_landmarks.landmark[idx]
            return (int(lm.x * w), int(lm.y * h))

        def line(a, b, color, t=2):
            cv2.line(frame, pt(a), pt(b), color, t)

        def dot(a, color, r=4):
            cv2.circle(frame, pt(a), r, color, -1)
            cv2.circle(frame, pt(a), r + 1, (255, 255, 255), 1)

        # Palm connections
        palm_ids = [0, 1, 5, 9, 13, 17, 0]
        for i in range(len(palm_ids) - 1):
            line(palm_ids[i], palm_ids[i+1], self.finger_colors['palm'], 2)

        # Fingers: (connection list, color key)
        fingers = [
            ([1, 2, 3, 4],    'thumb'),
            ([5, 6, 7, 8],    'index'),
            ([9, 10, 11, 12], 'middle'),
            ([13, 14, 15, 16],'ring'),
            ([17, 18, 19, 20],'pinky'),
        ]
        for ids, color_key in fingers:
            color = self.finger_colors[color_key]
            for i in range(len(ids) - 1):
                line(ids[i], ids[i+1], color, 2)
            for idx in ids:
                dot(idx, color)

        # Palm dots
        for idx in [0, 5, 9, 13, 17]:
            dot(idx, self.finger_colors['palm'])

    def find_pose(self, frame, draw=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # --- POSE ---
        pose_results = self.pose.process(rgb)
        if pose_results.pose_landmarks:
            self.landmarks = pose_results.pose_landmarks.landmark
            if draw:
                self.mp_draw.draw_landmarks(
                    frame,
                    pose_results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    self.mp_draw.DrawingSpec(color=(0, 200, 0), thickness=2)
                )

        # --- FACE MESH ---
        face_results = self.face_mesh.process(rgb)
        if face_results.multi_face_landmarks and draw:
            for face_lms in face_results.multi_face_landmarks:
                self.mp_draw.draw_landmarks(
                    image=frame,
                    landmark_list=face_lms,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_draw_styles
                        .get_default_face_mesh_tesselation_style()
                )
                self.mp_draw.draw_landmarks(
                    image=frame,
                    landmark_list=face_lms,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_draw_styles
                        .get_default_face_mesh_contours_style()
                )

        # --- HANDS (finger colors) ---
        hand_results = self.hands.process(rgb)
        if hand_results.multi_hand_landmarks and draw:
            for hand_lms in hand_results.multi_hand_landmarks:
                self.draw_fingers(frame, hand_lms)

        return frame

    def get_landmark(self, index, frame_shape):
        if self.landmarks:
            h, w = frame_shape[:2]
            lm = self.landmarks[index]
            return int(lm.x * w), int(lm.y * h)
        return None

    def is_detected(self):
        return self.landmarks is not None
    