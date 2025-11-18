#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
خدمة Keep-Alive للحفاظ على البوت مستيقظاً على Render
تعمل كـ Web Server بسيط يستجيب لطلبات HTTP
"""

from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# معلومات البوت
BOT_INFO = {
    "name": "Telegram Quiz Bot",
    "description": "بوت اختبارات أساسيات شبكات الحاسب",
    "questions_count": 34,
    "bot_username": "@cs_networks_bot",
    "version": "2.0",
    "features": [
        "34 سؤال في شبكات الحاسب",
        "انتقال تلقائي للأسئلة",
        "إحصائيات مفصلة",
        "يعمل 24/7 على Render"
    ]
}

@app.route('/')
def home():
    """الصفحة الرئيسية - عرض معلومات البوت"""
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{BOT_INFO['name']}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            
            .container {{
                background: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 600px;
                width: 100%;
                backdrop-filter: blur(10px);
            }}
            
            h1 {{
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-align: center;
            }}
            
            .emoji {{
                font-size: 3em;
                text-align: center;
                margin-bottom: 20px;
            }}
            
            .status {{
                background: #4ade80;
                color: white;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 30px;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
            }}
            
            .info {{
                background: #f3f4f6;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            
            .info-item {{
                display: flex;
                align-items: center;
                margin-bottom: 15px;
                padding: 10px;
                background: white;
                border-radius: 8px;
            }}
            
            .info-item:last-child {{
                margin-bottom: 0;
            }}
            
            .info-icon {{
                font-size: 1.5em;
                margin-left: 15px;
            }}
            
            .info-text {{
                flex: 1;
                color: #374151;
            }}
            
            .features {{
                background: #f3f4f6;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            
            .features h2 {{
                color: #667eea;
                margin-bottom: 15px;
                text-align: center;
            }}
            
            .feature-item {{
                background: white;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 10px;
                color: #374151;
            }}
            
            .feature-item:last-child {{
                margin-bottom: 0;
            }}
            
            .cta {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border-radius: 10px;
                text-align: center;
                font-size: 1.1em;
                font-weight: bold;
                text-decoration: none;
                display: block;
                transition: transform 0.3s;
            }}
            
            .cta:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            }}
            
            .footer {{
                text-align: center;
                margin-top: 30px;
                color: #6b7280;
                font-size: 0.9em;
            }}
            
            .timestamp {{
                text-align: center;
                margin-top: 20px;
                color: #9ca3af;
                font-size: 0.85em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🤖</div>
            <h1>{BOT_INFO['name']}</h1>
            
            <div class="status">
                ✅ البوت يعمل بنجاح!
            </div>
            
            <div class="info">
                <div class="info-item">
                    <span class="info-icon">📚</span>
                    <span class="info-text"><strong>الوصف:</strong> {BOT_INFO['description']}</span>
                </div>
                <div class="info-item">
                    <span class="info-icon">📊</span>
                    <span class="info-text"><strong>عدد الأسئلة:</strong> {BOT_INFO['questions_count']} سؤال</span>
                </div>
                <div class="info-item">
                    <span class="info-icon">🔗</span>
                    <span class="info-text"><strong>اسم البوت:</strong> {BOT_INFO['bot_username']}</span>
                </div>
                <div class="info-item">
                    <span class="info-icon">🚀</span>
                    <span class="info-text"><strong>الإصدار:</strong> {BOT_INFO['version']}</span>
                </div>
            </div>
            
            <div class="features">
                <h2>✨ المميزات</h2>
                {''.join([f'<div class="feature-item">✓ {feature}</div>' for feature in BOT_INFO['features']])}
            </div>
            
            <a href="https://t.me/{BOT_INFO['bot_username'][1:]}" class="cta" target="_blank">
                افتح البوت في Telegram
            </a>
            
            <div class="footer">
                <p>🌐 يعمل على Render</p>
                <p>💚 مفتوح المصدر</p>
            </div>
            
            <div class="timestamp">
                آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """نقطة فحص صحة البوت"""
    return jsonify({
        "status": "healthy",
        "bot": "running",
        "timestamp": datetime.now().isoformat(),
        "service": "telegram-quiz-bot"
    }), 200

@app.route('/ping')
def ping():
    """نقطة Ping بسيطة"""
    return jsonify({
        "message": "pong",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/status')
def status():
    """معلومات حالة البوت"""
    return jsonify({
        "bot_info": BOT_INFO,
        "status": "active",
        "uptime": "running",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/info')
def api_info():
    """API للحصول على معلومات البوت"""
    return jsonify(BOT_INFO), 200

def run_server():
    """تشغيل خادم Flask"""
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    run_server()
