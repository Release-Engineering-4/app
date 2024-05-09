function checkFraud() {
    var input = document.getElementById("inputField").value;
    var result = document.getElementById("result");
    var inputDisplay = document.getElementById("inputDisplay");
    
    if (input === "") {
        result.innerHTML = "Please enter a value";
        inputDisplay.innerHTML = "Input: " + input;
        return;
    }
    // Perform fraud detection logic here
    // Replace the following line with your actual fraud detection code
    var isFraud = Math.random() < 0.5;
    
    inputDisplay.innerHTML = "Input: " + input;
    
    if (isFraud > 0.5) {
        result.innerHTML = "Fraud";
    } else {
        result.innerHTML = "Not Fraud";
    }
}
