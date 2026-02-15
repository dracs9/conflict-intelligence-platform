"""
OCR Vision Service
Extracts dialogue from chat screenshots
"""
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
from typing import List, Dict, Tuple
import re

class OCRService:
    """OCR and chat bubble detection service"""
    
    def __init__(self):
        # Configure tesseract if needed
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        pass
    
    def process_chat_screenshot(self, image_bytes: bytes) -> List[Dict]:
        """
        Process chat screenshot and extract structured dialogue
        Returns list of dialogue turns with speaker detection
        """
        
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(image)
        
        # Convert to OpenCV format
        if len(img_array.shape) == 2:
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif img_array.shape[2] == 4:
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        else:
            img_cv = img_array.copy()
        
        # Detect chat bubbles
        bubbles = self._detect_chat_bubbles(img_cv)
        
        # Extract text from each bubble
        turns = []
        for i, bubble in enumerate(bubbles):
            text = self._extract_text_from_region(img_cv, bubble)
            
            if text.strip():
                turns.append({
                    "turn_id": i,
                    "speaker": bubble["speaker"],
                    "text": text.strip(),
                    "position": bubble["position"],
                    "alignment": bubble["alignment"]
                })
        
        return turns
    
    def _detect_chat_bubbles(self, image: np.ndarray) -> List[Dict]:
        """
        Detect chat bubbles using color clustering and position
        """
        height, width = image.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to detect text regions
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bubbles = []
        
        for contour in contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter small regions
            if w < 50 or h < 20:
                continue
            
            # Determine speaker based on horizontal position
            center_x = x + w / 2
            
            if center_x < width * 0.4:
                speaker = "user"
                alignment = "left"
            elif center_x > width * 0.6:
                speaker = "opponent"
                alignment = "right"
            else:
                # Middle region - use color to determine
                roi = image[y:y+h, x:x+w]
                avg_color = roi.mean(axis=0).mean(axis=0)
                
                # Simple heuristic: lighter colors on right (iOS style)
                if avg_color.mean() > 180:
                    speaker = "opponent"
                    alignment = "right"
                else:
                    speaker = "user"
                    alignment = "left"
            
            bubbles.append({
                "bbox": (x, y, w, h),
                "speaker": speaker,
                "alignment": alignment,
                "position": {
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h
                }
            })
        
        # Sort bubbles by vertical position (top to bottom)
        bubbles.sort(key=lambda b: b["position"]["y"])
        
        return bubbles
    
    def _extract_text_from_region(self, image: np.ndarray, bubble: Dict) -> str:
        """Extract text from a bubble region using OCR"""
        
        x, y, w, h = bubble["bbox"]
        
        # Add padding
        padding = 5
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        # Extract ROI
        roi = image[y:y+h, x:x+w]
        
        # Preprocess for better OCR
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        roi_thresh = cv2.adaptiveThreshold(
            roi_gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # OCR
        try:
            text = pytesseract.image_to_string(roi_thresh, config='--psm 6')
            
            # Clean text
            text = self._clean_ocr_text(text)
            
            return text
        except Exception as e:
            print(f"OCR error: {e}")
            return ""
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean OCR artifacts"""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR errors
        text = text.replace('|', 'I')
        text = text.replace('0', 'O')  # Only in words
        
        # Strip
        text = text.strip()
        
        return text
    
    def extract_text_simple(self, image_bytes: bytes) -> str:
        """Simple text extraction without bubble detection"""
        
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to grayscale
        gray_image = image.convert('L')
        
        # OCR
        text = pytesseract.image_to_string(gray_image)
        
        return self._clean_ocr_text(text)
