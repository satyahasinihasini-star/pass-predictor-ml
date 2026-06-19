const studySlider = document.getElementById('study_hours');
const attendanceSlider = document.getElementById('attendance');
const marksSlider = document.getElementById('previous_marks');

const valStudy = document.getElementById('val-study');
const valAttendance = document.getElementById('val-attendance');
const valMarks = document.getElementById('val-marks');

const runBtn = document.getElementById('runBtn');
const needle = document.getElementById('needle');
const gaugeFill = document.getElementById('gaugeFill');
const gaugePercent = document.getElementById('gaugePercent');
const stamp = document.getElementById('stamp');
const historyList = document.getElementById('historyList');

const GAUGE_CIRCUMFERENCE = 314; // matches stroke-dasharray in CSS

studySlider.addEventListener('input', () => {
  valStudy.textContent = parseFloat(studySlider.value).toFixed(1);
});
attendanceSlider.addEventListener('input', () => {
  valAttendance.textContent = attendanceSlider.value + '%';
});
marksSlider.addEventListener('input', () => {
  valMarks.textContent = marksSlider.value + '%';
});

function setGauge(percent) {
  // needle sweeps from -90deg (0%) to +90deg (100%)
  const angle = -90 + (percent / 100) * 180;
  needle.style.transform = `rotate(${angle}deg)`;

  const offset = GAUGE_CIRCUMFERENCE - (percent / 100) * GAUGE_CIRCUMFERENCE;
  gaugeFill.style.strokeDashoffset = offset;

  gaugePercent.textContent = percent.toFixed(1) + '%';
}

function setStamp(result) {
  stamp.textContent = result;
  stamp.classList.remove('pass', 'fail');
  stamp.classList.add(result === 'PASS' ? 'pass' : 'fail');
}

function renderHistory(items) {
  if (!items.length) {
    historyList.innerHTML = '<div class="history-empty">No predictions yet — run one above.</div>';
    return;
  }
  historyList.innerHTML = items.map(item => `
    <div class="history-item">
      <span class="h-inputs">${item.study_hours}h · ${item.attendance}% att · ${item.previous_marks}% prev</span>
      <span class="h-result ${item.result === 'PASS' ? 'pass' : 'fail'}">${item.result} · ${item.probability}%</span>
    </div>
  `).join('');
}

async function loadHistory() {
  try {
    const res = await fetch('/history');
    const data = await res.json();
    renderHistory(data);
  } catch (err) {
    console.error('Failed to load history', err);
  }
}

async function runPrediction() {
  runBtn.disabled = true;
  runBtn.querySelector('span').textContent = 'Running...';

  const payload = {
    study_hours: studySlider.value,
    attendance: attendanceSlider.value,
    previous_marks: marksSlider.value
  };

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    setGauge(data.probability);
    setStamp(data.result);
    loadHistory();
  } catch (err) {
    console.error('Prediction failed', err);
    alert('Something went wrong. Is the Flask server running?');
  } finally {
    runBtn.disabled = false;
    runBtn.querySelector('span').textContent = 'Run Prediction';
  }
}

runBtn.addEventListener('click', runPrediction);

// load existing history on page load
loadHistory();
