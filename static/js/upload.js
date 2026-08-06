// Upload handling functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeUploadArea();
    initializeFileInput();
});

function initializeUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const clearBtn = document.getElementById('clearBtn');
    
    if (!uploadArea || !fileInput) return;
    
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File selected
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    });
    
    // Analyze button
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeImage);
    }
    
    // Clear button
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAll);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFiles(files) {
    const file = files[0];
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/tiff'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Unsupported file format. Please upload JPG, PNG, WEBP, or TIFF files.', 'danger');
        return;
    }
    
    // Validate file size (100MB)
    if (file.size > 100 * 1024 * 1024) {
        showNotification('File size exceeds 100MB limit.', 'danger');
        return;
    }
    
    // Display file info
    displayFileInfo(file);
    
    // Enable analyze button
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
    }
}

function displayFileInfo(file) {
    const fileInfoDiv = document.getElementById('fileInfo');
    if (!fileInfoDiv) return;
    
    fileInfoDiv.innerHTML = `
        <div class="glass-card">
            <h5><i class="fas fa-file-image"></i> Selected File</h5>
            <p><strong>Name:</strong> ${file.name}</p>
            <p><strong>Type:</strong> ${file.type}</p>
            <p><strong>Size:</strong> ${formatFileSize(file.size)}</p>
        </div>
    `;
    
    fileInfoDiv.style.display = 'block';
}

function showLoading() {
    const loadingDiv = document.getElementById('loadingAnimation');
    if (loadingDiv) {
        loadingDiv.innerHTML = `
            <div class="text-center">
                <div class="loader"></div>
                <p class="mt-3">Analyzing image...</p>
                <div class="progress mt-3">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 100%"></div>
                </div>
            </div>
        `;
        loadingDiv.style.display = 'block';
    }
}

function hideLoading() {
    const loadingDiv = document.getElementById('loadingAnimation');
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }
}

async function analyzeImage() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput || !fileInput.files[0]) {
        showNotification('Please select an image first.', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    showLoading();
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        const data = await response.json();
        currentAnalysisData = data;
        
        // Display results
        displayResults(data);
        hideLoading();
        showNotification('Analysis complete!', 'success');
        
    } catch (error) {
        hideLoading();
        showNotification(error.message, 'danger');
    }
}

function displayResults(data) {
    const resultsDiv = document.getElementById('analysisResults');
    if (!resultsDiv) return;
    
    resultsDiv.style.display = 'block';
    
    // Display file information
    displayFileAnalysis(data.file_info);
    
    // Display EXIF data
    displayExifData(data.exif_data);
    
    // Display GPS data
    displayGPSData(data.gps_data);
    
    // Display hashes
    displayHashes(data.hashes);
    
    // Display image analysis
    displayImageAnalysis(data.image_analysis);
    
    // Display OCR text
    displayOCRText(data.ocr_text);
    
    // Display security analysis
    displaySecurityAnalysis(data.security_analysis);
    
    // Display metadata summary
    displayMetadataSummary(data.metadata_summary);
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

function displayFileAnalysis(fileInfo) {
    const div = document.getElementById('fileAnalysis');
    if (!div) return;
    
    div.innerHTML = `
        <div class="glass-card">
            <h4><i class="fas fa-info-circle"></i> File Information</h4>
            <div class="row mt-3">
                <div class="col-md-6">
                    <p><strong>Filename:</strong> ${fileInfo.filename}</p>
                    <p><strong>Size:</strong> ${fileInfo.size_formatted}</p>
                    <p><strong>Extension:</strong> ${fileInfo.extension}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Width:</strong> ${fileInfo.width || 'N/A'}px</p>
                    <p><strong>Height:</strong> ${fileInfo.height || 'N/A'}px</p>
                    <p><strong>Resolution:</strong> ${fileInfo.resolution || 'N/A'}</p>
                </div>
            </div>
        </div>
    `;
}

function displayExifData(exifData) {
    const div = document.getElementById('exifData');
    if (!div) return;
    
    if (!exifData.available) {
        div.innerHTML = `
            <div class="glass-card">
                <h4><i class="fas fa-camera"></i> EXIF Metadata</h4>
                <p class="text-muted mt-3">No EXIF Metadata Found</p>
            </div>
        `;
        return;
    }
    
    let exifHTML = '<div class="glass-card"><h4><i class="fas fa-camera"></i> EXIF Metadata</h4><div class="table-responsive mt-3"><table class="table table-dark table-hover">';
    exifHTML += '<thead><tr><th>Tag</th><th>Value</th></tr></thead><tbody>';
    
    for (const [key, value] of Object.entries(exifData.data)) {
        exifHTML += `<tr><td>${key}</td><td>${value}</td></tr>`;
    }
    
    exifHTML += '</tbody></table></div></div>';
    div.innerHTML = exifHTML;
}

function displayGPSData(gpsData) {
    const div = document.getElementById('gpsData');
    if (!div) return;
    
    if (!gpsData.available) {
        div.innerHTML = `
            <div class="glass-card">
                <h4><i class="fas fa-map-marker-alt"></i> GPS Location</h4>
                <p class="text-muted mt-3">No GPS Location Available</p>
            </div>
        `;
        return;
    }
    
    div.innerHTML = `
        <div class="glass-card">
            <h4><i class="fas fa-map-marker-alt"></i> GPS Location</h4>
            <div class="row mt-3">
                <div class="col-md-6">
                    <p><strong>Latitude:</strong> ${gpsData.latitude}</p>
                    <p><strong>Longitude:</strong> ${gpsData.longitude}</p>
                    <p><strong>Altitude:</strong> ${gpsData.altitude || 'N/A'}</p>
                </div>
                <div class="col-md-6">
                    <button class="btn btn-sm btn-cyber mb-2" onclick="window.open('https://www.google.com/maps?q=${gpsData.latitude},${gpsData.longitude}', '_blank')">
                        <i class="fab fa-google"></i> Google Maps
                    </button>
                    <button class="btn btn-sm btn-cyber mb-2" onclick="copyToClipboard('${gpsData.latitude}, ${gpsData.longitude}')">
                        <i class="fas fa-copy"></i> Copy Coordinates
                    </button>
                </div>
            </div>
            <div id="map" style="height: 400px; margin-top: 20px;"></div>
        </div>
    `;
    
    // Initialize map
    setTimeout(() => {
        initMap(gpsData.latitude, gpsData.longitude);
    }, 100);
}

function displayHashes(hashes) {
    const div = document.getElementById('hashData');
    if (!div) return;
    
    let hashHTML = '<div class="glass-card"><h4><i class="fas fa-shield-alt"></i> Cryptographic Hashes</h4>';
    
    for (const [algo, value] of Object.entries(hashes)) {
        hashHTML += `
            <div class="mt-3">
                <strong>${algo.toUpperCase()}:</strong>
                <div class="hash-value">${value}</div>
                <button class="btn btn-sm btn-outline-info" onclick="copyToClipboard('${value}')">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
        `;
    }
    
    hashHTML += '</div>';
    div.innerHTML = hashHTML;
}

function displayImageAnalysis(analysis) {
    const div = document.getElementById('imageAnalysis');
    if (!div) return;
    
    div.innerHTML = `
        <div class="glass-card">
            <h4><i class="fas fa-chart-bar"></i> Image Analysis</h4>
            <div class="row mt-3">
                <div class="col-md-4">
                    <div class="info-card">
                        <h6>Brightness</h6>
                        <p class="h4">${analysis.brightness}</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="info-card">
                        <h6>Contrast</h6>
                        <p class="h4">${analysis.contrast}</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="info-card">
                        <h6>Sharpness</h6>
                        <p class="h4">${analysis.sharpness}</p>
                    </div>
                </div>
            </div>
            
            <div class="mt-4">
                <h6>Dominant Colors</h6>
                <div class="color-palette">
                    ${analysis.dominant_colors.map(color => `
                        <div class="color-swatch" style="background-color: ${color.hex}" title="${color.hex} - ${color.percentage}"></div>
                    `).join('')}
                </div>
            </div>
            
            <div class="mt-3">
                <p><strong>Noise Level:</strong> ${analysis.noise_estimation}</p>
                <p><strong>Compression:</strong> ${analysis.compression_estimation}</p>
                <p><strong>Entropy:</strong> ${analysis.entropy}</p>
            </div>
        </div>
    `;
}

function displayOCRText(ocrData) {
    const div = document.getElementById('ocrData');
    if (!div) return;
    
    if (!ocrData.available) {
        div.innerHTML = `
            <div class="glass-card">
                <h4><i class="fas fa-font"></i> OCR Text Extraction</h4>
                <p class="text-muted mt-3">No text detected</p>
            </div>
        `;
        return;
    }
    
    div.innerHTML = `
        <div class="glass-card">
            <h4><i class="fas fa-font"></i> OCR Text Extraction</h4>
            <div class="mt-3">
                <p><strong>Word Count:</strong> ${ocrData.word_count}</p>
                <p><strong>Character Count:</strong> ${ocrData.character_count}</p>
            </div>
            <div class="mt-3 p-3" style="background: rgba(0,0,0,0.3); border-radius: 10px; max-height: 200px; overflow-y: auto;">
                <pre style="color: white; margin: 0;">${ocrData.text || 'No text detected'}</pre>
            </div>
            <button class="btn btn-sm btn-cyber mt-2" onclick="copyToClipboard('${ocrData.text.replace(/'/g, "\\'")}')">
                <i class="fas fa-copy"></i> Copy Text
            </button>
        </div>
    `;
}

function displaySecurityAnalysis(security) {
    const div = document.getElementById('securityAnalysis');
    if (!div) return;
    
    const riskColor = {
        'Green': 'risk-green',
        'Yellow': 'risk-yellow',
        'Red': 'risk-red'
    };
    
    div.innerHTML = `
        <div class="glass-card">
            <h4><i class="fas fa-shield-haltered"></i> Security Analysis</h4>
            <div class="mt-3">
                <h5>Risk Level: <span class="${riskColor[security.risk_indicator.level]}">${security.risk_indicator.level}</span></h5>
                <p>Confidence: ${security.risk_indicator.confidence}</p>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <p><i class="fas fa-${security.metadata_available ? 'check-circle risk-green' : 'times-circle risk-red'}"></i> Metadata Available</p>
                    <p><i class="fas fa-${security.gps_available ? 'check-circle risk-green' : 'times-circle risk-red'}"></i> GPS Available</p>
                    <p><i class="fas fa-${security.edited_software_detected ? 'exclamation-triangle risk-yellow' : 'check-circle risk-green'}"></i> Edited Software Detected</p>
                </div>
                <div class="col-md-6">
                    <p><i class="fas fa-${security.likely_screenshot ? 'check-circle risk-green' : 'times-circle risk-red'}"></i> Likely Screenshot</p>
                    <p><i class="fas fa-${security.likely_camera_photo ? 'check-circle risk-green' : 'times-circle risk-red'}"></i> Likely Camera Photo</p>
                    <p><i class="fas fa-${security.possible_social_media_compression ? 'exclamation-triangle risk-yellow' : 'check-circle risk-green'}"></i> Social Media Compression</p>
                </div>
            </div>
        </div>
    `;
}

function displayMetadataSummary(summary) {
    const div = document.getElementById('metadataSummary');
    if (!div) return;
    
    div.innerHTML = `
        <div class="glass-card">
            <h4><i class="fas fa-clipboard-list"></i> Metadata Summary</h4>
            <div class="row mt-3">
                <div class="col-md-4">
                    <div class="info-card">
                        <h6>Camera</h6>
                        <p>${summary.camera_used}</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="info-card">
                        <h6>Date/Time</h6>
                        <p>${summary.captured_date} ${summary.captured_time}</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="info-card">
                        <h6>GPS Status</h6>
                        <p>${summary.gps_status}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function clearAll() {
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const results = document.getElementById('analysisResults');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.style.display = 'none';
    if (results) results.style.display = 'none';
    if (analyzeBtn) analyzeBtn.disabled = true;
    
    currentAnalysisData = null;
    showNotification('Cleared all data', 'info');
}