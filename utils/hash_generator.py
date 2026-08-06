import hashlib

class HashGenerator:
    def __init__(self, image_path):
        self.image_path = image_path
        self.hashes = self._generate_hashes()
    
    def _generate_hashes(self):
        """Generate all cryptographic hashes"""
        hashes = {}
        
        with open(self.image_path, 'rb') as f:
            data = f.read()
            
            hashes['md5'] = hashlib.md5(data).hexdigest()
            hashes['sha1'] = hashlib.sha1(data).hexdigest()
            hashes['sha256'] = hashlib.sha256(data).hexdigest()
            hashes['sha512'] = hashlib.sha512(data).hexdigest()
        
        return hashes
    
    def get_all_hashes(self):
        """Return all generated hashes"""
        return self.hashes
    
    def verify_hash(self, hash_type, expected_hash):
        """Verify hash against expected value"""
        if hash_type in self.hashes:
            return self.hashes[hash_type] == expected_hash
        return False