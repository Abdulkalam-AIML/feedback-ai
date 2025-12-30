let pieChart = null;
let barChart = null;

async function uploadCSV() {
  const fileInput = document.getElementById("bulkFile");

  if (!fileInput.files.length) {
    alert("Please upload a CSV file");
    return;
  }

  const form = new FormData();
  form.append("file", fileInput.files[0]);

  const res = await fetch("/upload-feedback", {
    method: "POST",
    body: form
  });

  const data = await res.json();

  // ✅ SAFETY CHECK
  if (data.error) {
    alert(data.error);
    return;
  }

  // ✅ Update numbers
  document.getElementById("total").innerText = data.total;
  document.getElementById("pos").innerText =
    `${data.positive} (${data.positive_pct}%)`;
  document.getElementById("neu").innerText =
    `${data.neutral} (${data.neutral_pct}%)`;
  document.getElementById("neg").innerText =
    `${data.negative} (${data.negative_pct}%)`;

  document.getElementById("overall").innerText =
    `🧠 Overall Review: ${data.overall}`;

  // 🧹 Destroy old charts
  if (pieChart) pieChart.destroy();
  if (barChart) barChart.destroy();

  // 🥧 PIE CHART
  pieChart = new Chart(document.getElementById("pieChart"), {
    type: "pie",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [{
        data: [data.positive, data.neutral, data.negative],
        backgroundColor: ["#22c55e", "#9ca3af", "#ef4444"]
      }]
    }
  });

  // 📊 BAR CHART
  barChart = new Chart(document.getElementById("barChart"), {
    type: "bar",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [{
        label: "Feedback Count",
        data: [data.positive, data.neutral, data.negative],
        backgroundColor: ["#22c55e", "#9ca3af", "#ef4444"]
      }]
    }
  });
}
async function trainModel() {
  const fileInput = document.getElementById("trainFile");

  if (!fileInput.files.length) {
    alert("Please upload training CSV");
    return;
  }

  const form = new FormData();
  form.append("file", fileInput.files[0]);

  const res = await fetch("/train-model", {
    method: "POST",
    body: form
  });

  const data = await res.json();

  if (data.error) {
    document.getElementById("trainStatus").innerText =
      "❌ " + data.error;
    return;
  }

  document.getElementById("trainStatus").innerText =
    "✅ Model trained successfully. You can now analyze feedback.";
}
async function testModel() {
  const file = document.getElementById("testFile").files[0];
  if (!file) {
    alert("Upload test dataset");
    return;
  }

  const form = new FormData();
  form.append("file", file);

  const res = await fetch("/test-model", {
    method: "POST",
    body: form
  });

  const data = await res.json();

  if (data.error) {
    alert(data.error);
    return;
  }

  document.getElementById("testOverall").innerText =
    `📊 Test Result: ${data.overall}
     😊 ${data.positive_pct}% | 😐 ${data.neutral_pct}% | 😡 ${data.negative_pct}%`;

  // reuse charts
  if (window.testPie) window.testPie.destroy();

  window.testPie = new Chart(document.getElementById("pieChart"), {
    type: "doughnut",
    data: {
      labels: ["😊 Positive", "😐 Neutral", "😡 Negative"],
      datasets: [{
        data: [data.positive, data.neutral, data.negative],
        backgroundColor: ["#22c55e", "#9ca3af", "#ef4444"]
      }]
    }
  });
}














































