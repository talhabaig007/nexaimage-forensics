from PIL import Image
import os

class SecurityAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
    
    def analyze(self):
        """Perform security analysis on image"""
        exif_present = self._check_exif()
        gps_present = self._check_gps()
        edited = self._detect_editing()
        metadata_removed = not exif_present and self._was_metadata_likely_removed()
        screenshot = self._is_likely_screenshot()
        camera_photo = self._is_likely_camera_photo()
        social_media = self._detect_social_media_compression()
        
        # Calculate risk score
        risk_factors = 0
        if exif_present: risk_factors += 1
        if gps_present: risk_factors += 1
        if edited: risk_factors -= 1
        if social_media: risk_factors -= 1
        
        risk_level = 'Green' if risk_factors >= 2 else 'Yellow' if risk_factors >= 1 else 'Red'
        
        return {
            'metadata_available': exif_present,
            'gps_available': gps_present,
            'edited_software_detected': edited,
            'metadata_removed': metadata_removed,
            'likely_screenshot': screenshot,
            'likely_camera_photo': camera_photo,
            'possible_social_media_compression': social_media,
            'risk_indicator': {
                'level': risk_level,
                'confidence': f"{abs(risk_factors) / 3 * 100:.1f}%"
            }
        }
    
    def _check_exif(self):
        """Check if EXIF data exists"""
        return bool(self.image._getexif())
    
    def _check_gps(self):
        """Check for GPS data"""
        exif = self.image._getexif()
        if exif:
            return 34853 in exif  # GPSInfo tag
        return False
    
    def _detect_editing(self):
        """Detect if image was edited with software"""
        exif = self.image._getexif()
        if exif:
            software = exif.get(305)  # Software tag
            return bool(software)
        return False
    
    def _was_metadata_likely_removed(self):
        """Check if metadata was likely removed"""
        # Check file structure for signs of metadata stripping
        return not self._check_exif() and self.image.format in ['JPEG', 'TIFF']
    
    def _is_likely_screenshot(self):
        """Determine if image is likely a screenshot"""
        width, height = self.image.size
        common_screen_resolutions = [
            (1920, 1080), (1366, 768), (1440, 900),
            (1536, 864), (1280, 720), (2560, 1440)
        ]
        return (width, height) in common_screen_resolutions
    
    def _is_likely_camera_photo(self):
        """Determine if image is likely from a camera"""
        return self._check_exif() and not self._is_likely_screenshot()
    
    def _detect_social_media_compression(self):
        """Detect if image might have been compressed by social media"""
        # Check file size vs dimensions for compression signs
        width, height = self.image.size
        file_size = os.path.getsize(self.image_path)
        
        # Rough heuristic: social media compressed images are often small
        # for their dimensions
        expected_size = (width * height * 3) / 1024  # Rough KB estimate
        actual_size_kb = file_size / 1024
        
        return actual_size_kb < (expected_size * 0.3)  # 70% smaller than expected