const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const resultDiv = document.getElementById('result');
const scanButton = document.getElementById('scan-button');
let scanInterval;

scanButton.addEventListener('click', () => {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } }).then(stream => {
        video.srcObject = stream;
        video.play();

        scanInterval = setInterval(() => {
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = canvas.toDataURL('image/png');
            fetch('/scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image: imageData.split(',')[1] })
            }).then(response => response.json()).then(data => {
                if (data.barcode) {
                    clearInterval(scanInterval);
                    stream.getTracks().forEach(track => track.stop());
                    video.hidden = true;
                    sessionStorage.setItem('barcode', data.barcode);
                    window.location.href = `/result/${data.barcode}`;
                }
            }).catch(error => {
                console.error('Error:', error);
            });
        }, 500);
    }).catch(err => {
        console.error('Error accessing camera:', err);
        resultDiv.innerHTML = "카메라 접근에 실패했습니다.";
    });
});
