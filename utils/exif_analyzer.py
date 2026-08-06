from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
from datetime import datetime
import json

class ExifAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.exif_data = self._extract_exif()
        
    def _extract_exif(self):
        """Extract EXIF data from image"""
        exif_data = {}
        try:
            info = self.image._getexif()
            if info:
                for tag_id, value in info.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'GPSInfo':
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = str(gps_value)
                        exif_data[tag] = gps_data
                    else:
                        # Convert bytes to string if needed
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8')
                            except:
                                value = str(value)
                        exif_data[tag] = str(value)
        except:
            pass
        
        # Try piexif for more comprehensive extraction
        try:
            piexif_data = piexif.load(self.image.info.get('exif', b''))
            for ifd_name in piexif_data:
                if ifd_name != 'thumbnail':
                    for tag in piexif_data[ifd_name]:
                        tag_name = piexif.TAGS[ifd_name][tag]["name"]
                        value = piexif_data[ifd_name][tag]
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8')
                            except:
                                value = str(value)
                        exif_data[tag_name] = str(value)
        except:
            pass
            
        return exif_data
    
    def get_all_exif(self):
        """Return all EXIF data"""
        if not self.exif_data:
            return {"available": False, "message": "No EXIF Metadata Found"}
        return {"available": True, "data": self.exif_data}
    
    def get_gps_data(self):
        """Extract GPS coordinates if available"""
        gps_info = {}
        
        try:
            if 'GPSInfo' in self.exif_data:
                gps_data = self.exif_data['GPSInfo']
                
                # Convert GPS coordinates
                def convert_to_degrees(value):
                    if isinstance(value, str):
                        # Parse the string representation
                        import re
                        numbers = re.findall(r'\d+\.?\d*', value)
                        if len(numbers) >= 3:
                            d = float(numbers[0])
                            m = float(numbers[1])
                            s = float(numbers[2])
                            return d + (m / 60.0) + (s / 3600.0)
                    return 0
                
                if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                    lat = convert_to_degrees(gps_data['GPSLatitude'])
                    lon = convert_to_degrees(gps_data['GPSLongitude'])
                    
                    # Check for N/S/E/W
                    if 'GPSLatitudeRef' in gps_data and gps_data['GPSLatitudeRef'] != 'N':
                        lat = -lat
                    if 'GPSLongitudeRef' in gps_data and gps_data['GPSLongitudeRef'] != 'W':
                        lon = -lon
                    
                    gps_info = {
                        'available': True,
                        'latitude': lat,
                        'longitude': lon,
                        'altitude': gps_data.get('GPSAltitude', 'N/A')
                    }
                else:
                    gps_info = {'available': False}
            else:
                gps_info = {'available': False}
        except:
            gps_info = {'available': False}
            
        return gps_info
    
    def get_metadata_summary(self):
        """Generate metadata summary cards"""
        summary = {
            'camera_used': self.exif_data.get('Model', 'Unknown'),
            'captured_date': self.exif_data.get('DateTimeOriginal', 'Unknown'),
            'captured_time': self.exif_data.get('DateTimeOriginal', 'Unknown').split()[1] if 'DateTimeOriginal' in self.exif_data and ' ' in self.exif_data['DateTimeOriginal'] else 'Unknown',
            'software_used': self.exif_data.get('Software', 'None detected'),
            'gps_status': 'Available' if self.get_gps_data().get('available') else 'Not Available',
            'metadata_status': 'Present' if self.exif_data else 'Not Available',
            'image_orientation': self.exif_data.get('Orientation', 'Unknown'),
            'image_type': self.exif_data.get('MIMEType', 'Unknown')
        }
        return summary