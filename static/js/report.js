// Report generation functionality

async function generateReport() {
    if (!currentAnalysisData) {
        showNotification('No analysis data available. Please analyze an image first.', 'warning');
        return;
    }
    
    showNotification('Generating PDF report...', 'info');
    
    try {
        const response = await fetch('/api/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentAnalysisData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate report');
        }
        
        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `forensic_report_${new Date().toISOString().slice(0, 10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('Report generated successfully!', 'success');
        
    } catch (error) {
        showNotification('Error generating report: ' + error.message, 'danger');
    }
}