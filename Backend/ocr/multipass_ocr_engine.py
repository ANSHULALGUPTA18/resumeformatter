"""
LAYER 2: Multi-Pass OCR Engine (EasyOCR Edition)
Performs specialized OCR passes for different resume sections using EasyOCR

Key Improvements over Tesseract:
- Higher accuracy on designed/formatted resumes
- Built-in text detection and recognition
- Confidence scores per text box
- No OpenCV dependency issues (Windows-safe)
- Multi-language support built-in
- No cv2 DLL dependencies

Architecture:
- Pass 1: Header-optimized (candidate name, contact info)
- Pass 2: Section headers (EMPLOYMENT, EDUCATION, etc.)
- Pass 3: Body content (detailed text)

Each pass uses EasyOCR with region-specific cropping and preprocessing
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, List, Tuple, Optional
import re


class MultiPassOCREngine:
    """Performs multiple specialized OCR passes using EasyOCR for optimal text extraction"""

    def __init__(self, use_gpu: bool = False):
        """
        Initialize EasyOCR engine

        Args:
            use_gpu: Whether to use GPU acceleration (requires CUDA)
        """
        # Lazy import EasyOCR to avoid startup overhead
        import easyocr

        # Initialize EasyOCR with optimal settings for resume processing
        # EasyOCR doesn't have OpenCV DLL issues on Windows
        self.reader = easyocr.Reader(
            ['en'],              # English language
            gpu=use_gpu,         # GPU acceleration if available
            verbose=False        # Suppress verbose logs
        )

        print("[OCR] EasyOCR engine initialized successfully (Windows-safe, no cv2 DLL issues)")

    def perform_multipass_ocr(self, image_path: str, layout_info: Dict) -> Dict:
        """
        Main method: Perform all three OCR passes using EasyOCR

        Args:
            image_path: Path to resume image or PIL Image
            layout_info: Layout analysis from Layer 1

        Returns:
            {
                'header_ocr': {...},
                'section_headers_ocr': [...],
                'body_ocr': [...],
                'full_text': str
            }
        """
        # Load image
        if isinstance(image_path, str):
            pil_img = Image.open(image_path)
        else:
            pil_img = image_path

        # Convert to RGB if needed (EasyOCR expects RGB)
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')

        # Pass 1: Header extraction
        header_result = self._pass1_header_ocr(pil_img, layout_info)

        # Pass 2: Section headers
        section_headers_result = self._pass2_section_headers_ocr(pil_img, layout_info)

        # Pass 3: Body content
        body_result = self._pass3_body_content_ocr(pil_img, layout_info)

        # Combine all text in reading order
        full_text = self._combine_results(header_result, section_headers_result, body_result, layout_info)

        return {
            'header_ocr': header_result,
            'section_headers_ocr': section_headers_result,
            'body_ocr': body_result,
            'full_text': full_text,
            'ocr_method': 'easyocr_multipass'
        }

    def _pass1_header_ocr(self, pil_img: Image.Image, layout_info: Dict) -> Dict:
        """
        Pass 1: Extract header information (name, contact)
        Uses aggressive preprocessing for top zone
        """
        print("  [Pass 1] Extracting header with EasyOCR...")

        # Crop to header zone
        zones = layout_info['zones']
        header_end = zones['header'][1]
        header_img = pil_img.crop((0, 0, pil_img.width, header_end))

        # Preprocessing for header (enhance name/contact visibility)
        preprocessed = self._preprocess_for_header(header_img)

        # Run EasyOCR on header region
        try:
            # Convert PIL to numpy array for EasyOCR
            img_array = np.array(preprocessed)

            # Run OCR
            result = self.reader.readtext(img_array)

            # Extract text and confidence
            if result:
                text_lines = []
                confidences = []

                for detection in result:
                    # EasyOCR returns: (bbox, text, confidence)
                    bbox, text, conf = detection[0], detection[1], detection[2]
                    text_lines.append(text)
                    confidences.append(conf)

                combined_text = '\n'.join(text_lines)
                avg_confidence = np.mean(confidences) * 100 if confidences else 0
            else:
                combined_text = ""
                avg_confidence = 0

        except Exception as e:
            print(f"  [WARN] Header OCR error: {e}")
            combined_text = ""
            avg_confidence = 0

        return {
            'text': combined_text.strip(),
            'confidence': avg_confidence,
            'zone': 'header',
            'method': 'easyocr_header'
        }

    def _pass2_section_headers_ocr(self, pil_img: Image.Image, layout_info: Dict) -> List[Dict]:
        """
        Pass 2: Extract section headers only
        Uses EasyOCR's text detection on heading regions
        """
        print("  [Pass 2] Extracting section headers with EasyOCR...")

        headings = layout_info['headings']
        results = []

        for i, heading in enumerate(headings):
            # Crop to heading bbox
            x, y, w, h = heading['bbox']
            heading_img = pil_img.crop((x, y, x + w, y + h))

            # Preprocess for heading (enhance contrast, bold text)
            preprocessed = self._preprocess_for_heading(heading_img)

            # Run EasyOCR
            try:
                img_array = np.array(preprocessed)
                result = self.reader.readtext(img_array)

                if result:
                    # Combine all detected text in this heading
                    text_parts = []
                    confidences = []

                    for detection in result:
                        # EasyOCR returns: (bbox, text, confidence)
                        bbox, text, conf = detection[0], detection[1], detection[2]
                        text_parts.append(text)
                        confidences.append(conf)

                    text = ' '.join(text_parts)
                    avg_confidence = np.mean(confidences) * 100 if confidences else 0
                else:
                    text = ""
                    avg_confidence = 0

            except Exception as e:
                print(f"  [WARN] Heading {i} OCR error: {e}")
                text = ""
                avg_confidence = 0

            results.append({
                'text': text.strip(),
                'original_bbox': heading['bbox'],
                'confidence': avg_confidence,
                'is_heading': True,
                'heading_index': i
            })

        return results

    def _pass3_body_content_ocr(self, pil_img: Image.Image, layout_info: Dict) -> List[Dict]:
        """
        Pass 3: Extract body content
        Uses EasyOCR on text blocks
        """
        print("  [Pass 3] Extracting body content with EasyOCR...")

        text_blocks = layout_info['text_blocks']
        results = []

        # Filter out headings (already processed in Pass 2)
        body_blocks = [block for block in text_blocks if not block.get('is_heading', False)]

        for i, block in enumerate(body_blocks):
            # Crop to block bbox
            x, y, w, h = block['bbox']

            # Add padding
            padding = 5
            x_start = max(0, x - padding)
            y_start = max(0, y - padding)
            x_end = min(pil_img.width, x + w + padding)
            y_end = min(pil_img.height, y + h + padding)

            block_img = pil_img.crop((x_start, y_start, x_end, y_end))

            # Preprocess for body content
            preprocessed = self._preprocess_for_body(block_img)

            # Run EasyOCR
            try:
                img_array = np.array(preprocessed)
                result = self.reader.readtext(img_array)

                if result:
                    # Sort text by y-coordinate to maintain reading order
                    text_items = []
                    for detection in result:
                        # EasyOCR returns: (bbox, text, confidence)
                        # bbox is (x1,y1,x2,y2,x3,y3,x4,y4)
                        bbox, text, conf = detection[0], detection[1], detection[2]
                        # Get y-coordinate of text box (top-left y)
                        y_pos = bbox[1]  # y1 coordinate
                        text_items.append((y_pos, text, conf))

                    # Sort by y-position
                    text_items.sort(key=lambda x: x[0])

                    # Combine text
                    text_lines = [item[1] for item in text_items]
                    confidences = [item[2] for item in text_items]

                    text = '\n'.join(text_lines)
                    avg_confidence = np.mean(confidences) * 100 if confidences else 0
                else:
                    text = ""
                    avg_confidence = 0

            except Exception as e:
                print(f"  [WARN] Block {i} OCR error: {e}")
                text = ""
                avg_confidence = 0

            if text:  # Only include non-empty blocks
                results.append({
                    'text': text.strip(),
                    'original_bbox': block['bbox'],
                    'confidence': avg_confidence,
                    'is_heading': False,
                    'block_index': i,
                    'reading_order': block.get('reading_order', i)
                })

        return results

    def _preprocess_for_header(self, img: Image.Image) -> Image.Image:
        """
        Preprocessing optimized for header (name, contact)
        Uses Pillow-only operations - NO OpenCV
        """
        # Convert to grayscale
        img = img.convert('L')

        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)

        # Denoise
        img = img.filter(ImageFilter.MedianFilter(size=3))

        # Convert back to RGB for EasyOCR
        return img.convert('RGB')

    def _preprocess_for_heading(self, img: Image.Image) -> Image.Image:
        """
        Preprocessing optimized for section headings
        Uses Pillow + NumPy - NO OpenCV
        """
        # Convert to grayscale
        img = img.convert('L')

        # Strong contrast enhancement (headings are often bold)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)

        # Sharpen
        img = img.filter(ImageFilter.SHARPEN)

        # Simple threshold to binary using NumPy (replaces cv2.threshold)
        img_array = np.array(img)

        # Otsu's thresholding algorithm (pure NumPy implementation)
        threshold = self._otsu_threshold(img_array)
        binary = np.where(img_array > threshold, 255, 0).astype(np.uint8)

        img = Image.fromarray(binary)

        # Convert back to RGB for EasyOCR
        return img.convert('RGB')

    def _preprocess_for_body(self, img: Image.Image) -> Image.Image:
        """
        Preprocessing optimized for body text
        Uses Pillow + NumPy - NO OpenCV
        """
        # Convert to grayscale
        img = img.convert('L')

        # Moderate contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)

        # Light denoising
        img = img.filter(ImageFilter.MedianFilter(size=3))

        # Adaptive threshold using NumPy (replaces cv2.adaptiveThreshold)
        img_array = np.array(img)
        binary = self._adaptive_threshold(img_array, block_size=11, c=2)

        img = Image.fromarray(binary)

        # Convert back to RGB for EasyOCR
        return img.convert('RGB')

    def _otsu_threshold(self, img_array: np.ndarray) -> int:
        """
        Otsu's thresholding algorithm (pure NumPy implementation)
        Replaces cv2.threshold with THRESH_OTSU

        Args:
            img_array: Grayscale image as numpy array

        Returns:
            Optimal threshold value
        """
        # Flatten image
        pixels = img_array.flatten()

        # Calculate histogram
        hist, bin_edges = np.histogram(pixels, bins=256, range=(0, 256))
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Calculate cumulative sums
        weight1 = np.cumsum(hist)
        weight2 = np.cumsum(hist[::-1])[::-1]

        # Calculate cumulative means
        mean1 = np.cumsum(hist * bin_centers) / weight1
        mean2 = (np.cumsum((hist * bin_centers)[::-1]) / weight2[::-1])[::-1]

        # Calculate between-class variance
        variance = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2

        # Find maximum variance
        idx = np.argmax(variance)
        threshold = bin_centers[:-1][idx]

        return int(threshold)

    def _adaptive_threshold(self, img_array: np.ndarray, block_size: int = 11, c: int = 2) -> np.ndarray:
        """
        Adaptive thresholding using local mean (pure NumPy + scipy)
        Replaces cv2.adaptiveThreshold

        Args:
            img_array: Grayscale image as numpy array
            block_size: Size of local neighborhood
            c: Constant subtracted from mean

        Returns:
            Binary image as numpy array
        """
        from scipy.ndimage import uniform_filter

        # Calculate local mean using uniform filter
        local_mean = uniform_filter(img_array.astype(float), size=block_size)

        # Threshold: pixel > (local_mean - c)
        binary = np.where(img_array > (local_mean - c), 255, 0).astype(np.uint8)

        return binary

    def _combine_results(self, header_result: Dict, section_headers: List[Dict],
                        body_results: List[Dict], layout_info: Dict) -> str:
        """
        Combine all OCR results in correct reading order

        Priority:
        1. Header text
        2. Section headers and body content in reading order (by y-coordinate)
        """
        combined_text = []

        # Add header
        if header_result['text']:
            combined_text.append(header_result['text'])
            combined_text.append('')  # Blank line

        # Combine section headers and body, sort by reading order
        all_content = []

        # Add section headers
        for header in section_headers:
            all_content.append({
                'text': header['text'],
                'y': header['original_bbox'][1],
                'is_heading': True
            })

        # Add body content
        for body in body_results:
            all_content.append({
                'text': body['text'],
                'y': body['original_bbox'][1],
                'is_heading': False
            })

        # Sort by y-coordinate (top to bottom)
        all_content.sort(key=lambda x: x['y'])

        # Build text with proper spacing
        for item in all_content:
            if item['is_heading']:
                combined_text.append('')  # Blank line before heading
                combined_text.append(item['text'].upper())  # Headings in CAPS
                combined_text.append('')  # Blank line after heading
            else:
                combined_text.append(item['text'])

        return '\n'.join(combined_text)

    def correct_low_confidence_text(self, text: str, confidence: float) -> str:
        """
        Apply corrections to low-confidence OCR text
        Fixes common OCR errors
        """
        if confidence >= 80:
            return text  # High confidence, no correction needed

        # Common OCR error corrections
        corrections = {
            r'\bl\b': 'I',  # lowercase L to uppercase I
            r'0': 'O',  # zero to letter O (in words)
            r'5': 'S',  # five to S (in words)
            r'8': 'B',  # eight to B (in words)
            r'\s+': ' ',  # Multiple spaces to single
        }

        corrected = text
        for pattern, replacement in corrections.items():
            corrected = re.sub(pattern, replacement, corrected)

        return corrected


# Utility function
def perform_ocr_multipass(image_path: str, layout_info: Dict, use_gpu: bool = False) -> Dict:
    """
    Convenience function for multi-pass OCR using EasyOCR

    Args:
        image_path: Path to resume image
        layout_info: Layout analysis dictionary
        use_gpu: Whether to use GPU acceleration

    Returns:
        OCR results dictionary
    """
    engine = MultiPassOCREngine(use_gpu=use_gpu)
    return engine.perform_multipass_ocr(image_path, layout_info)


if __name__ == "__main__":
    import sys
    from visual_layout_analyzer import analyze_resume_image

    if len(sys.argv) > 1:
        print("Analyzing layout...")
        layout = analyze_resume_image(sys.argv[1])

        print("\nPerforming multi-pass OCR with EasyOCR...")
        result = perform_ocr_multipass(sys.argv[1], layout)

        print(f"\nHeader confidence: {result['header_ocr']['confidence']:.1f}%")
        print(f"Section headers found: {len(result['section_headers_ocr'])}")
        print(f"Body blocks found: {len(result['body_ocr'])}")

        print("\n" + "="*60)
        print("EXTRACTED TEXT:")
        print("="*60)
        print(result['full_text'])
