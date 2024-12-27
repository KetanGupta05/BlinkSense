let currentStream = null; 


function fetchBlinkCount() {
    fetch('/get_blink_count') 
        .then(response => response.json())
        .then(data => {
          
            document.getElementById('blink-count').innerText = 'Blink Count: ' + data.blink_count;

            
            if (data.reminder) {
                showNotification("Time to Blink!", "Your blink count is low. Remember to blink!");
            }
        })
        .catch(error => console.error("Error fetching blink count:", error));
}

// Function to show a desktop notification
function showNotification(title, message) {
    if (Notification.permission === "granted") {
        new Notification(title, { body: message });
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                new Notification(title, { body: message });
            }
        });
    }
}

window.onload = function () {
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
};


setInterval(fetchBlinkCount, 1000);  
