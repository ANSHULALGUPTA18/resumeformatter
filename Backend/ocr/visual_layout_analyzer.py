"""
LAYER 1: Visual Layout Analyzer (EasyOCR Edition)
Extracts visual structure from resume images using EasyOCR's layout detection

Key Improvements:
- Uses EasyOCR's built-in text detection for accurate bounding boxes
- No OpenCV DLL dependency issues (Windows-safe)
- More reliable heading detection using EasyOCR's confidence scores
- Faster layout analysis with optimized detection settings
- No cv2 DLL errors on Windows

Features:
- Detects zones (header, body sections)
- Identifies headings by size, boldness, position
- Detects multi-column layouts
- Creates reading order map
- Preserves spatial coordinates
"""

import numpy as np
from PIL import Image, ImageStat
from typing import List, Dict, Tuple, Optional


class VisualLayoutAnalyzer:
    """Analyzes visual layout of resume images using EasyOCR"""

    def __init__(self):
        self.header_zone_threshold = 0.15  # Top 15% is header
        self.column_gap_threshold = 50  # Min pixels between columns
        self.heading_size_ratio = 1.3  # Headings are 30%+ larger

        # Lazy load EasyOCR
        import easyocr
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    def analyze_layout(self, image_path: str) -> Dict:
        """
        Main method: Analyze visual layout of resume image

        Returns:
            {
                'zones': {...},
                'text_blocks': [...],
                'headings': [...],
                'columns': {...},
                'reading_order': [...]
            }
        """
        # Load image
        if isinstance(image_path, str):
            pil_img = Image.open(image_path)
        else:
            # Already PIL Image
            pil_img = image_path

        # Convert to RGB if needed
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')

        width, height = pil_img.size

        # Step 1: Detect zones
        zones = self._detect_zones(height)

        # Step 2: Extract text blocks with coordinates using PaddleOCR
        text_blocks = self._extract_text_blocks(pil_img)

        # Step 3: Detect columns
        columns = self._detect_columns(text_blocks, width)

        # Step 4: Identify headings
        headings = self._identify_headings(text_blocks, pil_img)

        # Step 5: Create reading order
        reading_order = self._create_reading_order(text_blocks, columns)

        return {
            'zones': zones,
            'text_blocks': text_blocks,
            'headings': headings,
            'columns': columns,
            'reading_order': reading_order,
            'image_size': (width, height)
        }

    def _detect_zones(self, height: int) -> Dict:
        """Detect page zones (header, body)"""
        header_end = int(height * self.header_zone_threshold)

        return {
            'header': (0, header_end),
            'body': (header_end, height)
        }

    def _extract_text_blocks(self, pil_img: Image.Image) -> List[Dict]:
        """
        Extract text blocks with bounding boxes using EasyOCR
        Each block contains: text, coordinates, confidence
        """
        # Convert PIL to numpy array for EasyOCR
        img_array = np.array(pil_img)

        # Run EasyOCR to get text detection results
        try:
            result = self.reader.readtext(img_array)
        except Exception as e:
            print(f"  [WARN] Layout analysis OCR error: {e}")
            return []

        text_blocks = []

        if not result:
            return text_blocks

        # Convert EasyOCR results to text blocks
        for idx, detection in enumerate(result):
            # EasyOCR returns: (bbox, text, confidence)
            # bbox is (x1,y1,x2,y2,x3,y3,x4,y4) - flat tuple of 8 coordinates
            bbox, text, conf = detection[0], detection[1], detection[2]

            # Convert bbox to (x, y, width, height)
            # bbox is (x1,y1, x2,y2, x3,y3, x4,y4)
            x_coords = [bbox[0], bbox[2], bbox[4], bbox[6]]
            y_coords = [bbox[1], bbox[3], bbox[5], bbox[7]]

            x = int(min(x_coords))
            y = int(min(y_coords))
            w = int(max(x_coords) - x)
            h = int(max(y_coords) - y)

            # Determine zone
            zone = 'header' if y < pil_img.height * self.header_zone_threshold else 'body'

            text_blocks.append({
                'text': text,
                'bbox': (x, y, w, h),
                'confidence': conf * 100,  # EasyOCR returns 0-1, convert to 0-100
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'is_heading': False,  # Will be determined later
                'zone': zone,
                'block_num': idx,
                'line_num': idx
            })

        return text_blocks

    def _detect_columns(self, text_blocks: List[Dict], page_width: int) -> Dict:
        """
        Detect if resume has multiple columns
        Returns column boundaries
        """
        if not text_blocks:
            return {'count': 1, 'boundaries': [(0, page_width)]}

        # Create histogram of x-coordinates
        hist = np.zeros(page_width, dtype=int)
        for block in text_blocks:
            x_start = block['x']
            x_end = block['x'] + block['width']
            hist[x_start:min(x_end, page_width)] += 1

        # Find vertical gaps (potential column separators)
        gaps = []
        in_gap = False
        gap_start = 0

        for x in range(page_width):
            if hist[x] == 0:
                if not in_gap:
                    gap_start = x
                    in_gap = True
            else:
                if in_gap:
                    gap_width = x - gap_start
                    if gap_width > self.column_gap_threshold:
                        gaps.append((gap_start, x))
                    in_gap = False

        # If significant gap found, assume 2-column layout
        if gaps:
            # Use largest gap as column divider
            largest_gap = max(gaps, key=lambda g: g[1] - g[0])
            mid_point = (largest_gap[0] + largest_gap[1]) // 2

            return {
                'count': 2,
                'boundaries': [(0, mid_point), (mid_point, page_width)],
                'divider': mid_point
            }

        return {'count': 1, 'boundaries': [(0, page_width)]}

    def _identify_headings(self, text_blocks: List[Dict], img: Image.Image) -> List[Dict]:
        """
        Identify which text blocks are headings based on:
        - Font size (height)
        - Boldness (pixel density)
        - Position (isolated)
        - ALL CAPS
        """
        if not text_blocks:
            return []

        # Calculate average text height
        heights = [block['height'] for block in text_blocks if block['height'] > 0]
        if not heights:
            return []

        avg_height = np.median(heights)

        headings = []

        for i, block in enumerate(text_blocks):
            is_heading = False
            reasons = []

            # Check 1: Size (height is significantly larger)
            if block['height'] > avg_height * self.heading_size_ratio:
                is_heading = True
                reasons.append('size')

            # Check 2: ALL CAPS
            if block['text'].isupper() and len(block['text'].split()) <= 5:
                is_heading = True
                reasons.append('all_caps')

            # Check 3: Boldness (estimate from pixel density)
            boldness = self._estimate_boldness(img, block['bbox'])
            if boldness > 1.2:  # 20% denser than average
                is_heading = True
                reasons.append('bold')

            # Check 4: Short text (headings are typically short)
            word_count = len(block['text'].split())
            if word_count <= 4 and block['height'] > avg_height * 1.1:
                is_heading = True
                reasons.append('short')

            # Check 5: Common section keywords
            section_keywords = [
                'employment', 'experience', 'work', 'education', 'skills',
                'summary', 'profile', 'objective', 'projects', 'certifications',
                'achievements', 'awards', 'languages', 'history', 'background'
            ]
            text_lower = block['text'].lower()
            if any(kw in text_lower for kw in section_keywords):
                if word_count <= 5:
                    is_heading = True
                    reasons.append('keyword')

            if is_heading:
                block['is_heading'] = True
                block['heading_reasons'] = reasons
                headings.append(block)

        return headings

    def _estimate_boldness(self, img: Image.Image, bbox: Tuple) -> float:
        """
        Estimate if text is bold by analyzing pixel density
        Uses Pillow-only operations - NO OpenCV

        Returns ratio: block_density / image_average_density
        """
        try:
            x, y, w, h = bbox

            # Extract block region
            block_img = img.crop((x, y, x + w, y + h))

            # Convert to grayscale
            if block_img.mode != 'L':
                gray_block = block_img.convert('L')
            else:
                gray_block = block_img

            # Calculate density (ratio of dark pixels)
            # Use ImageStat to get mean brightness
            stat = ImageStat.Stat(gray_block)
            block_mean = stat.mean[0]

            # Calculate overall image brightness
            gray_img = img.convert('L')
            stat_full = ImageStat.Stat(gray_img)
            img_mean = stat_full.mean[0]

            # Darker text has lower mean brightness
            # Inverted ratio: darker blocks have higher "density"
            if block_mean == 0:
                return 1.0

            # Estimate boldness: inverse of brightness ratio
            density_ratio = img_mean / block_mean

            return density_ratio

        except Exception as e:
            # print(f"  ⚠️ Boldness estimation error: {e}")
            return 1.0

    def _create_reading_order(self, text_blocks: List[Dict], columns: Dict) -> List[int]:
        """
        Create reading order based on layout
        For 2-column: read left column top-to-bottom, then right column
        For 1-column: top-to-bottom
        Returns: list of block indices in reading order
        """
        if not text_blocks:
            return []

        if columns['count'] == 1:
            # Simple top-to-bottom
            sorted_blocks = sorted(enumerate(text_blocks), key=lambda x: (x[1]['y'], x[1]['x']))
            return [idx for idx, _ in sorted_blocks]

        elif columns['count'] == 2:
            divider = columns['divider']

            # Separate into left and right columns
            left_blocks = []
            right_blocks = []

            for idx, block in enumerate(text_blocks):
                block_center = block['x'] + block['width'] / 2
                if block_center < divider:
                    left_blocks.append((idx, block))
                else:
                    right_blocks.append((idx, block))

            # Sort each column top-to-bottom
            left_blocks.sort(key=lambda x: (x[1]['y'], x[1]['x']))
            right_blocks.sort(key=lambda x: (x[1]['y'], x[1]['x']))

            # Combine: left column first, then right
            reading_order = [idx for idx, _ in left_blocks] + [idx for idx, _ in right_blocks]
            return reading_order

        return list(range(len(text_blocks)))

    def get_blocks_in_zone(self, text_blocks: List[Dict], zone: str) -> List[Dict]:
        """Get all text blocks in a specific zone"""
        return [block for block in text_blocks if block.get('zone') == zone]

    def get_blocks_by_reading_order(self, text_blocks: List[Dict], reading_order: List[int]) -> List[Dict]:
        """Get text blocks sorted by reading order"""
        return [text_blocks[i] for i in reading_order if i < len(text_blocks)]


# Utility functions
def analyze_resume_image(image_path: str) -> Dict:
    """Convenience function to analyze a resume image using EasyOCR"""
    analyzer = VisualLayoutAnalyzer()
    return analyzer.analyze_layout(image_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = analyze_resume_image(sys.argv[1])
        print(f"Zones: {result['zones']}")
        print(f"Columns: {result['columns']}")
        print(f"Text blocks found: {len(result['text_blocks'])}")
        print(f"Headings found: {len(result['headings'])}")
        print(f"\nHeadings:")
        for h in result['headings']:
            print(f"  - {h['text']} (reasons: {', '.join(h['heading_reasons'])})")
