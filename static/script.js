document.getElementById("uploadForm")
    .addEventListener("submit", async function (e) {

        e.preventDefault();

        let formData = new FormData(this);

        let response = await fetch("/predict", {

            method: "POST",

            body: formData
        });

        let data = await response.json();

        document.getElementById("result").innerHTML = `
  <h2>Prediction Result</h2>
  <p><strong>Predicted Role:</strong> ${data.predicted_role}</p>
  <p><strong>Confidence:</strong> ${data.confidence}</p>
  <p><strong>Skills Found:</strong> ${data.skills.join(", ")}</p>
  <p><strong>Resume Score:</strong> ${data.score}/100</p>
  <hr/>
  <p style="font-size:12px;color:gray">
    Model can predict: ${data.model_classes.join(" · ")}
  </p>
`;
    });

async function sendChat() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chat-box");

    chatBox.innerHTML += `
        <div class="chat-msg user"><strong>You:</strong> ${message}</div>`;
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    });

    const data = await response.json();

    chatBox.innerHTML += `
    <div class="chat-msg bot"><strong>AI:</strong> ${data.reply
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
        }</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("chat-input")
        .addEventListener("keypress", function (e) {
            if (e.key === "Enter") sendChat();
        });
});