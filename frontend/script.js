async function humanize() {
  const text = document.getElementById("input").value;
  const mode = document.getElementById("mode")?.value || "standard";
  const ultra = document.getElementById("ultra")?.checked || false;

  if (!text.trim()) {
    alert("Please enter some text");
    return;
  }

  try {
    const res = await fetch("https://humanizer-backend-2604.onrender.com/humanize",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      text: text,
      mode: mode,
      ultra: ultra
    })
  }
);


    const data = await res.json();

    console.log("API response:", data);

    document.getElementById("output").value = data.result || "";
    document.getElementById("score").innerText =
      "Human-Style Confidence: " + (data.human_style_confidence || 0) + "%";

  } catch (err) {
    console.error("API error:", err);
    alert("Backend connection failed. Check console.");
  }
}
