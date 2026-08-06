from PIL import Image, ImageStat
import cv2
import numpy as np
from collections import Counter

class ImageAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.cv_image = cv2.imread(image_path)
        
    def get_basic_info(self):
        """Get basic image information"""
        width, height = self.image.size
        aspect_ratio = width / height if height > 0 else 0
        
        info = {
            'width': width,
            'height': height,
            'resolution': f"{width}x{height}",
            'aspect_ratio': f"{aspect_ratio:.2f}",
            'image_format': self.image.format,
            'color_mode': self.image.mode,
            'dpi': self.image.info.get('dpi', (72, 72)),
            'mime_type': Image.MIME.get(self.image.format, 'unknown'),
            'bit_depth': self._get_bit_depth()
        }
        return info
    
    def _get_bit_depth(self):
        """Estimate bit depth"""
        mode_to_bits = {
            '1': 1,
            'L': 8,
            'P': 8,
            'RGB': 24,
            'RGBA': 32,
            'CMYK': 32
        }
        return mode_to_bits.get(self.image.mode, 8)
    
    def analyze_image(self):
        """Perform comprehensive image analysis"""
        # Convert PIL image to numpy array for analysis
        img_array = np.array(self.image)
        
        # Basic statistics
        if len(img_array.shape) == 3:
            mean_rgb = np.mean(img_array, axis=(0, 1))
            brightness = np.mean(img_array) / 255.0 * 100
        else:
            mean_rgb = [np.mean(img_array)] * 3
            brightness = np.mean(img_array) / 255.0 * 100
        
        # Contrast calculation
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.cv_image
        contrast = np.std(gray) / 128.0 * 100
        
        # Dominant colors
        dominant_colors = self._get_dominant_colors()
        
        # Noise estimation
        noise_level = self._estimate_noise()
        
        # Sharpness estimation
        sharpness = self._estimate_sharpness()
        
        # Histogram data
        histogram = self._get_histogram()
        
        # Compression estimation
        compression = self._estimate_compression()
        
        # File entropy
        entropy = self._calculate_entropy()
        
        return {
            'brightness': f"{brightness:.1f}%",
            'contrast': f"{contrast:.1f}%",
            'average_rgb': {
                'red': int(mean_rgb[0]) if len(mean_rgb) > 0 else 0,
                'green': int(mean_rgb[1]) if len(mean_rgb) > 1 else 0,
                'blue': int(mean_rgb[2]) if len(mean_rgb) > 2 else 0
            },
            'dominant_colors': dominant_colors,
            'noise_estimation': f"{noise_level:.1f}%",
            'sharpness': f"{sharpness:.1f}%",
            'compression_estimation': compression,
            'entropy': f"{entropy:.2f}",
            'histogram': histogram
        }
    
    def _get_dominant_colors(self, num_colors=5):
        """Extract dominant colors from image"""
        img = self.image.copy()
        img.thumbnail((100, 100))  # Reduce size for faster processing
        pixels = list(img.getdata())
        
        # Count color occurrences
        color_counts = Counter(pixels)
        dominant = color_counts.most_common(num_colors)
        
        colors = []
        for color, count in dominant:
            if isinstance(color, tuple):
                colors.append({
                    'rgb': color[:3],
                    'hex': '#{:02x}{:02x}{:02x}'.format(*color[:3]),
                    'percentage': f"{(count / len(pixels)) * 100:.1f}%"
                })
        
        return colors
    
    def _estimate_noise(self):
        """Estimate image noise level"""
        gray = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
        # Apply high-pass filter
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        noise = np.var(laplacian)
        # Normalize to percentage
        return min(noise / 10.0 * 100, 100)
    
    def _estimate_sharpness(self):
        """Estimate image sharpness"""
        gray = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = np.var(laplacian)
        return min(sharpness / 1000.0 * 100, 100)
    
    def _get_histogram(self):
        """Generate color histogram data"""
        hist_data = {}
        colors = ('blue', 'green', 'red')
        
        for i, color in enumerate(colors):
            hist = cv2.calcHist([self.cv_image], [i], None, [256], [0, 256])
            hist_data[color] = hist.flatten().tolist()
        
        return hist_data
    
    def _estimate_compression(self):
        """Estimate image compression level"""
        # Check for JPEG compression artifacts
        if self.image.format == 'JPEG':
            quality = 'High'  # Placeholder estimation
            return f"JPEG - {quality} compression"
        elif self.image.format == 'PNG':
            return "PNG - Lossless compression"
        else:
            return "Unknown compression"
    
    def _calculate_entropy(self):
        """Calculate file entropy"""
        with open(self.image_path, 'rb') as f:
            data = f.read()
        
        if not data:
            return 0
        
        entropy = 0
        for x in range(256):
            p_x = data.count(x) / len(data)
            if p_x > 0:
                entropy += -p_x * np.log2(p_x)
        
        return entropy