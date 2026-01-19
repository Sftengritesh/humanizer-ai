async function humanize() {
  const text = document.getElementById("input").value;
  const mode = document.getElementById("mode").value;
  const ultra = document.getElementById("ultra").checked;

  const res = await fetch("http://127.0.0.1:5000/humanize", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ text, mode, ultra })
  });

  const data = await res.json();

  document.getElementById("output").value = data.result;
  document.getElementById("score").innerText =
    "Human-Style Confidence: " + data.human_style_confidence + "%";
}
