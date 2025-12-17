const NUTRITION_INFO = {
    "Bar_One": [201, 21],
    "Gems": [50, 9],
    "Kit-Kat": [106, 11],
    "Milky_Bar": [137, 14]
};

const COLORS = {
    green: '#00FF00',
    blue: '#0000FF',
    yellow: '#FFFF00',
    orange: '#FFA500',
    red: '#FF0000'
};

const BBOX_COLORS = [
    'rgb(164, 120, 87)',
    'rgb(68, 148, 228)',
    'rgb(93, 97, 209)',
    'rgb(178, 182, 133)',
    'rgb(88, 159, 106)',
    'rgb(96, 202, 231)',
    'rgb(159, 124, 168)',
    'rgb(169, 162, 241)',
    'rgb(98, 118, 150)',
    'rgb(172, 176, 184)'
];

let currentImage = null;
let stream = null;
let liveStream = null;
let liveAnalysisInterval = null;
let lastFrameTime = 0;
let frameCount = 0;

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('uploadSection');
const cameraSection = document.getElementById('cameraSection');
const liveVideoSection = document.getElementById('liveVideoSection');
const previewSection = document.getElementById('previewSection');
const loadingSection = document.getElementById('loadingSection');
const errorSection = document.getElementById('errorSection');
const preview = document.getElementById('preview');
const video = document.getElementById('video');
const liveVideo = document.getElementById('liveVideo');
const liveCanvas = document.getElementById('liveCanvas');
const resultCanvas = document.getElementById('resultCanvas');
const liveResultCanvas = document.getElementById('liveResultCanvas');


uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleImageUpload(file);
    }
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleImageUpload(file);
    }
});

function handleImageUpload(file) {
    currentImage = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        preview.src = e.target.result;
        preview.onload = () => {

            resultCanvas.width = preview.naturalWidth;
            resultCanvas.height = preview.naturalHeight;
        };
        uploadSection.classList.add('hidden');
        previewSection.classList.remove('hidden');
        errorSection.classList.add('hidden');
        resultCanvas.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        video.srcObject = stream;
        uploadSection.classList.add('hidden');
        cameraSection.classList.remove('hidden');
        errorSection.classList.add('hidden');
    } catch (err) {
        showError('Camera access denied. Please allow camera access.');
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    cameraSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
}

async function startLiveVideo() {
    try {
        liveStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        liveVideo.srcObject = liveStream;


        liveVideo.onloadedmetadata = () => {
            liveResultCanvas.width = liveVideo.videoWidth;
            liveResultCanvas.height = liveVideo.videoHeight;
        };

        uploadSection.classList.add('hidden');
        liveVideoSection.classList.remove('hidden');
        errorSection.classList.add('hidden');


        document.getElementById('resultsEmpty').classList.add('hidden');
        document.getElementById('resultsContent').classList.remove('hidden');


        liveAnalysisInterval = setInterval(analyzeLiveFrame, 500);


        updateFPS();
    } catch (err) {
        showError('Camera access denied. Please allow camera access.');
    }
}

function stopLiveVideo() {
    if (liveStream) {
        liveStream.getTracks().forEach(track => track.stop());
        liveStream = null;
    }
    if (liveAnalysisInterval) {
        clearInterval(liveAnalysisInterval);
        liveAnalysisInterval = null;
    }


    const ctx = liveResultCanvas.getContext('2d');
    ctx.clearRect(0, 0, liveResultCanvas.width, liveResultCanvas.height);

    liveVideoSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');


    document.getElementById('resultsEmpty').classList.remove('hidden');
    document.getElementById('resultsContent').classList.add('hidden');
    frameCount = 0;
}

function updateFPS() {
    if (!liveStream) return;

    const now = performance.now();
    frameCount++;

    if (now - lastFrameTime >= 1000) {
        document.getElementById('fps').textContent = frameCount.toFixed(1);
        frameCount = 0;
        lastFrameTime = now;
    }

    requestAnimationFrame(updateFPS);
}

async function analyzeLiveFrame() {
    if (!liveVideo.videoWidth) return;

    liveCanvas.width = liveVideo.videoWidth;
    liveCanvas.height = liveVideo.videoHeight;
    const ctx = liveCanvas.getContext('2d');
    ctx.drawImage(liveVideo, 0, 0);

    liveCanvas.toBlob(async (blob) => {
        try {
            const reader = new FileReader();
            reader.onload = async (e) => {
                const base64Data = e.target.result.split(',')[1];


                const response = await fetch('http://localhost:8000/api/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        image_data: base64Data,
                        image_type: 'image/jpeg',
                        number_of_candies: 'analyzing'
                    })
                });

                const data = await response.json();
                const text = data.content.find(c => c.type === 'text')?.text || '{}';
                const cleanText = text.replace(/```json|```/g, '').trim();
                const detectionData = JSON.parse(cleanText);

                processResults(detectionData, 1);


                if (detectionData.detections && detectionData.detections.length > 0) {
                    drawLiveBoundingBoxes(detectionData.detections);
                } else {
                    clearLiveBoundingBoxes();
                }
            };
            reader.readAsDataURL(blob);
        } catch (err) {
            console.error('Live analysis error:', err);
        }
    }, 'image/jpeg', 0.8);
}

function captureImage() {
    const canvas = document.getElementById('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
        handleImageUpload(file);
        stopCamera();
    }, 'image/jpeg');
}

async function analyzeImage() {
    if (!currentImage) return;

    loadingSection.classList.remove('hidden');
    previewSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    try {
        const reader = new FileReader();
        reader.onload = async (e) => {
            const base64Data = e.target.result.split(',')[1];


            const response = await fetch('http://localhost:8000/api/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_data: base64Data,
                    image_type: currentImage.type,
                    number_of_candies: 'analyzing'
                })
            });

            const data = await response.json();
            const text = data.content.find(c => c.type === 'text')?.text || '{}';
            const cleanText = text.replace(/```json|```/g, '').trim();
            const detectionData = JSON.parse(cleanText);

            processResults(detectionData);


            if (detectionData.detections && detectionData.detections.length > 0) {
                drawBoundingBoxes(resultCanvas, preview, detectionData.detections);
            }
        };
        reader.readAsDataURL(currentImage);

    } catch (err) {
        console.error(err);
        showError('Failed to analyze image. Make sure your Python server is running on port 8000.');
        loadingSection.classList.add('hidden');
        previewSection.classList.remove('hidden');
    }
}

function processResults(detectionData, liveframe = 0) {
    const candyCounts = {};
    detectionData.detections.forEach(d => {
        const lookupKey = d.candy.replace(/ /g, '_');
        candyCounts[lookupKey] = (candyCounts[lookupKey] || 0) + 1;
    });

    let totalCalories = 0;
    let totalSugar = 0;
    Object.entries(candyCounts).forEach(([candy, count]) => {
        if (NUTRITION_INFO[candy]) {
            totalCalories += NUTRITION_INFO[candy][0] * count;
            totalSugar += NUTRITION_INFO[candy][1] * count;
        }
    });

    const riskLevel = classifyCalories(totalCalories);
    const totalCount = Object.values(candyCounts).reduce((a, b) => a + b, 0);

    displayResults({ candyCounts, totalCalories, totalSugar, riskLevel, totalCount });

    loadingSection.classList.add('hidden');
    if (!liveframe) {
        previewSection.classList.remove('hidden');
    }
}

function classifyCalories(total) {
    if (total <= 100) return { label: "Safe", color: COLORS.green };
    if (total <= 200) return { label: "Moderate", color: COLORS.blue };
    if (total <= 400) return { label: "High", color: COLORS.yellow };
    if (total <= 700) return { label: "Excessive", color: COLORS.orange };
    return { label: "Extreme", color: COLORS.red };
}

function displayResults(results) {
    document.getElementById('resultsEmpty').classList.add('hidden');
    document.getElementById('resultsContent').classList.remove('hidden');

    document.getElementById('totalCount').textContent = results.totalCount;
    document.getElementById('totalCalories').textContent = results.totalCalories;
    document.getElementById('totalSugar').textContent = results.totalSugar;

    const riskCard = document.getElementById('riskCard');
    const riskLevel = document.getElementById('riskLevel');
    riskCard.style.backgroundColor = results.riskLevel.color + '20';
    riskLevel.style.color = results.riskLevel.color;
    riskLevel.textContent = results.riskLevel.label;

    const candyList = document.getElementById('candyList');
    candyList.innerHTML = '';
    Object.entries(results.candyCounts).forEach(([candy, count]) => {
        const lookupKey = candy.replace(/ /g, '_');
        const nutrition = NUTRITION_INFO[lookupKey];

        if (!nutrition) return;

        const item = document.createElement('div');
        item.className = 'candy-item';
        item.innerHTML = `
        <span class="candy-name">${candy.replace(/_/g, ' ')}</span>
        <div class="candy-details">
            <span class="candy-calories">${nutrition[0] * count} cal</span>
            <span class="candy-count">×${count}</span>
        </div>
    `;
        candyList.appendChild(item);
    });

}

function showError(message) {
    document.getElementById('errorText').textContent = message;
    errorSection.classList.remove('hidden');
}

function drawBoundingBoxes(canvas, image, detections) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);


    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);


    detections.forEach((detection, idx) => {
        if (!detection.bbox) return;

        const [xmin, ymin, xmax, ymax] = detection.bbox;
        const color = BBOX_COLORS[idx % BBOX_COLORS.length];


        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(xmin, ymin, xmax - xmin, ymax - ymin);


        const label = `${detection.candy}: ${Math.round(detection.confidence * 100)}%`;
        ctx.font = '16px Arial';
        const textMetrics = ctx.measureText(label);
        const textHeight = 20;

        ctx.fillStyle = color;
        ctx.fillRect(xmin, Math.max(ymin - textHeight - 5, 0), textMetrics.width + 10, textHeight + 5);


        ctx.fillStyle = 'black';
        ctx.fillText(label, xmin + 5, Math.max(ymin - 8, textHeight - 3));
    });


    canvas.style.display = 'block';
    image.style.display = 'none';
}

function drawLiveBoundingBoxes(detections) {
    const ctx = liveResultCanvas.getContext('2d');
    ctx.clearRect(0, 0, liveResultCanvas.width, liveResultCanvas.height);


    const scaleX = liveResultCanvas.width / liveVideo.videoWidth;
    const scaleY = liveResultCanvas.height / liveVideo.videoHeight;

    detections.forEach((detection, idx) => {
        if (!detection.bbox) return;

        const [xmin, ymin, xmax, ymax] = detection.bbox;
        const color = BBOX_COLORS[idx % BBOX_COLORS.length];


        const x = xmin * scaleX;
        const y = ymin * scaleY;
        const w = (xmax - xmin) * scaleX;
        const h = (ymax - ymin) * scaleY;


        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(x, y, w, h);


        const label = `${detection.candy}: ${Math.round(detection.confidence * 100)}%`;
        ctx.font = '16px Arial';
        const textMetrics = ctx.measureText(label);
        const textHeight = 20;

        ctx.fillStyle = color;
        ctx.fillRect(x, Math.max(y - textHeight - 5, 0), textMetrics.width + 10, textHeight + 5);


        ctx.fillStyle = 'black';
        ctx.fillText(label, x + 5, Math.max(y - 8, textHeight - 3));
    });
}
function clearBoundingBoxes() {
    const ctx = resultCanvas.getContext('2d');
    ctx.clearRect(0, 0, resultCanvas.width, resultCanvas.height);
    resultCanvas.style.display = 'none';
    preview.style.display = 'block';
}

function clearLiveBoundingBoxes() {
    const ctx = liveResultCanvas.getContext('2d');
    ctx.clearRect(0, 0, liveResultCanvas.width, liveResultCanvas.height);
}

function goBackToUpload() {

    currentImage = null;
    preview.style.display = 'block'
    const ctx = resultCanvas.getContext('2d');
    ctx.clearRect(0, 0, resultCanvas.width, resultCanvas.height);
    resultCanvas.style.display = 'none';


    previewSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
    errorSection.classList.add('hidden');


    fileInput.value = '';


    document.getElementById('resultsEmpty').classList.remove('hidden');
    document.getElementById('resultsContent').classList.add('hidden');
        }
