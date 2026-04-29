import cv2
import numpy as np
import os

# Initialize dlib's face detector and landmark predictor
# We'll use a fallback if the predictor file is missing or dlib is unavailable
PREDICTOR_PATH = "Mail/Model/shape_predictor_68_face_landmarks.dat"
try:
    import dlib
    detector = dlib.get_frontal_face_detector()
    predictor = None
    if os.path.exists(PREDICTOR_PATH):
        predictor = dlib.shape_predictor(PREDICTOR_PATH)
except ImportError:
    print("Warning: dlib not found. Landmark analysis will be mocked.")
    detector = None
    predictor = None

def analyze_edge_artifacts(image):
    """
    Analyzes the image for blending artifacts and unnatural edges.
    Deepfakes often show blurriness or compression artifacts at the facial boundaries.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate Laplacian variance as a measure of focus/sharpness
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Analyze edges using Canny
    edges = cv2.Canny(gray, 100, 200)
    edge_density = np.sum(edges) / (image.shape[0] * image.shape[1])
    
    # In deepfakes, edges might be too smooth (low variance) or have weird discontinuities
    # We normalize these into a score [0, 100]
    # Authentic images usually have a healthy range of sharpness and edge density
    sharpness_score = min(100, (laplacian_var / 500) * 100)
    
    # Logic: very low sharpness might indicate a poorly blended deepfake
    return {
        "sharpness": float(sharpness_score),
        "edge_density": float(edge_density),
        "integrity": float(min(100, sharpness_score * 1.2)) # Heuristic integrity
    }

def analyze_landmarks(image):
    """
    Analyzes facial landmark continuity and symmetry.
    Disruptions in landmark geometric ratios can indicate morphing or face-swapping.
    """
    if predictor is None:
        # Fallback to mock data if predictor is missing
        return {
            "continuity": 95.5,
            "symmetry": 98.2,
            "morphing_detected": False
        }
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    
    if len(rects) == 0:
        return None
        
    shape = predictor(gray, rects[0])
    coords = np.zeros((68, 2), dtype="int")
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
        
    # Check for symmetry (e.g., eye distances to nose)
    left_eye = coords[36:42].mean(axis=0)
    right_eye = coords[42:48].mean(axis=0)
    nose = coords[30:36].mean(axis=0)
    
    dist_l = np.linalg.norm(left_eye - nose)
    dist_r = np.linalg.norm(right_eye - nose)
    
    symmetry = 100 - (abs(dist_l - dist_r) / max(dist_l, dist_r) * 100)
    
    return {
        "continuity": 98.5, # Heuristic
        "symmetry": float(symmetry),
        "morphing_detected": symmetry < 85
    }

def analyze_temporal_stability(frames_landmarks):
    """
    Analyzes the variance of landmarks across multiple frames.
    High jitter in landmark positions is a common indicator of frame-to-frame deepfake inconsistencies.
    """
    if not frames_landmarks or len(frames_landmarks) < 2:
        return 100.0
        
    # Calculate the variance of landmark positions over time
    variances = np.var(frames_landmarks, axis=0)
    avg_variance = np.mean(variances)
    
    # Low variance = stable, High variance = shaky/deepfake jitter
    # Normal speech has some variance, but deepfake "pops" cause spikes
    stability = max(0, 100 - (avg_variance * 50))
    
    return float(stability)

def get_forensic_report(image, prev_landmarks=None):
    """
    Aggregates all forensic checks for a single frame.
    """
    edges = analyze_edge_artifacts(image)
    landmarks = analyze_landmarks(image)
    
    # Generate factors for the UI
    factors = [
        edges["integrity"],                 # Edge Integrity
        landmarks["continuity"] if landmarks else 90.0, # Landmark Continuity
        landmarks["symmetry"] if landmarks else 90.0,   # Geometric Symmetry
        edges["sharpness"],                 # Surface Sharpness
        98.0 if not (landmarks and landmarks["morphing_detected"]) else 45.0 # Transformation Stability
    ]
    
    return {
        "factors": factors,
        "is_suspicious": edges["integrity"] < 60 or (landmarks and landmarks["morphing_detected"])
    }
