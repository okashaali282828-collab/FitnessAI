from flask import Flask, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Gym Trainer Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #0a0a0a, #1a1a2e);
            padding: 20px 30px;
            border-bottom: 2px solid #00ff64;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header h1 {
            font-size: 1.6rem;
            color: #00ff64;
            letter-spacing: 2px;
        }
        .live-badge {
            background: #00ff64;
            color: #000;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            padding: 24px;
        }
        .card {
            background: #111;
            border: 1px solid #222;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: border-color 0.3s;
        }
        .card:hover { border-color: #00ff64; }
        .card .label {
            font-size: 0.7rem;
            color: #888;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .card .value {
            font-size: 2.4rem;
            font-weight: bold;
            color: #00ff64;
        }
        .card .value.orange { color: #ffa500; }
        .card .value.cyan   { color: #00dcff; }
        .card .value.white  { color: #ffffff; }
        .bottom-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            padding: 0 24px 24px;
        }
        .chart-card {
            background: #111;
            border: 1px solid #222;
            border-radius: 12px;
            padding: 20px;
        }
        .chart-card h3 {
            color: #00ff64;
            font-size: 0.85rem;
            letter-spacing: 1px;
            margin-bottom: 16px;
            text-transform: uppercase;
        }
        .issues-list { list-style: none; }
        .issues-list li {
            padding: 10px 14px;
            margin: 6px 0;
            border-radius: 8px;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .issues-list li.bad  { background: #1a0000; border-left: 3px solid #ff4444; color: #ff8888; }
        .issues-list li.good { background: #001a00; border-left: 3px solid #00ff64; color: #00ff64; }
        .posture-bar-wrap {
            margin-top: 10px;
        }
        .posture-bar-bg {
            background: #222;
            border-radius: 20px;
            height: 24px;
            width: 100%;
            overflow: hidden;
            margin-top: 8px;
        }
        .posture-bar-fill {
            height: 100%;
            border-radius: 20px;
            transition: width 0.5s ease, background 0.5s;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            padding: 16px;
            color: #333;
            font-size: 0.75rem;
            border-top: 1px solid #1a1a1a;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏋️ AI GYM TRAINER — OKASHA</h1>
        <span class="live-badge">● LIVE</span>
    </div>

    <div class="grid">
        <div class="card">
            <div class="label">Total Reps</div>
            <div class="value" id="reps">0</div>
        </div>
        <div class="card">
            <div class="label">Timer</div>
            <div class="value cyan" id="timer">00:00</div>
        </div>
        <div class="card">
            <div class="label">Posture Score</div>
            <div class="value orange" id="posture">0%</div>
        </div>
        <div class="card">
            <div class="label">Best Score</div>
            <div class="value white" id="best">0%</div>
        </div>
    </div>

    <div class="bottom-grid">
        <!-- Rep History Chart -->
        <div class="chart-card">
            <h3>📈 Rep Progress</h3>
            <canvas id="repChart" height="160"></canvas>
        </div>

        <!-- Posture Issues -->
        <div class="chart-card">
            <h3>🧍 Posture Status</h3>
            <div class="posture-bar-wrap">
                <div style="color:#888; font-size:0.8rem;">Live Score</div>
                <div class="posture-bar-bg">
                    <div class="posture-bar-fill" id="postureBar" style="width:0%">0%</div>
                </div>
            </div>
            <br>
            <ul class="issues-list" id="issuesList">
                <li class="good">✅ Posture data wait kar raha hai...</li>
            </ul>
        </div>
    </div>

    <div class="footer">AI Gym Trainer — FA24-BCS-187 Muhammad Okasha</div>

    <script>
        const socket = io();

        // Rep chart setup
        const ctx = document.getElementById('repChart').getContext('2d');
        const repChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Reps',
                    data: [],
                    borderColor: '#00ff64',
                    backgroundColor: 'rgba(0,255,100,0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#00ff64'
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#666' }, grid: { color: '#1a1a1a' } },
                    y: { ticks: { color: '#666' }, grid: { color: '#1a1a1a' }, beginAtZero: true }
                }
            }
        });

        let repHistory = [];
        let timeLabels = [];

        socket.on('update', function(data) {
            // Cards
            document.getElementById('reps').textContent    = data.reps;
            document.getElementById('timer').textContent   = data.timer;
            document.getElementById('posture').textContent = data.posture + '%';
            document.getElementById('best').textContent    = data.best + '%';

            // Posture bar
            const bar = document.getElementById('postureBar');
            bar.style.width = data.posture + '%';
            bar.textContent = data.posture + '%';
            if (data.posture >= 75)      { bar.style.background = '#00ff64'; bar.style.color = '#000'; }
            else if (data.posture >= 50) { bar.style.background = '#ffa500'; bar.style.color = '#000'; }
            else                         { bar.style.background = '#ff4444'; bar.style.color = '#fff'; }

            // Issues list
            const ul = document.getElementById('issuesList');
            ul.innerHTML = '';
            if (data.issues && data.issues.length > 0) {
                data.issues.forEach(issue => {
                    ul.innerHTML += '<li class="bad">⚠️ ' + issue + '</li>';
                });
            } else {
                ul.innerHTML = '<li class="good">✅ Posture Perfect!</li>';
            }

            // Rep chart — update every 5 reps
            if (data.reps > 0 && (repHistory.length === 0 || data.reps !== repHistory[repHistory.length-1])) {
                repHistory.push(data.reps);
                timeLabels.push(data.timer);
                if (repHistory.length > 20) {
                    repHistory.shift();
                    timeLabels.shift();
                }
                repChart.data.labels   = timeLabels;
                repChart.data.datasets[0].data = repHistory;
                repChart.update();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

def send_update(reps, timer, posture, best, issues):
    socketio.emit('update', {
        'reps':    reps,
        'timer':   timer,
        'posture': posture,
        'best':    best,
        'issues':  issues
    })

def run_server():
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)