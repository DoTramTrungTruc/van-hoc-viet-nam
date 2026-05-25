import sys, os
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from config import Config

print("=== CẤU HÌNH EMAIL ===")
print(f"SERVER:   {Config.MAIL_SERVER}")
print(f"PORT:     {Config.MAIL_PORT}")
print(f"TLS:      {Config.MAIL_USE_TLS}")
print(f"USERNAME: {Config.MAIL_USERNAME}")
print(f"PASSWORD: {'*' * len(Config.MAIL_PASSWORD)} ({len(Config.MAIL_PASSWORD)} ký tự)")
print(f"FROM:     {Config.MAIL_FROM}")
print()

# Test kết nối SMTP
import smtplib
try:
    print("⏳ Đang kết nối SMTP...")
    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as s:
        s.ehlo()
        s.starttls()
        s.ehlo()
        print("✅ Kết nối TLS thành công")
        
        print("⏳ Đang đăng nhập...")
        s.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        print("✅ Đăng nhập thành công!")
        
        print("⏳ Đang gửi email test...")
        from email.mime.text import MIMEText
        msg = MIMEText("Test email từ Văn Học Việt Nam", "plain", "utf-8")
        msg["Subject"] = "Test SMTP"
        msg["From"]    = Config.MAIL_USERNAME
        msg["To"]      = Config.MAIL_USERNAME
        s.sendmail(Config.MAIL_USERNAME, Config.MAIL_USERNAME, msg.as_string())
        print("✅ Gửi email thành công!")

except smtplib.SMTPAuthenticationError as e:
    print(f"❌ LỖI XÁC THỰC: {e}")
    print("→ App Password sai hoặc chưa bật 2FA")
except smtplib.SMTPConnectError as e:
    print(f"❌ LỖI KẾT NỐI: {e}")
    print("→ Kiểm tra firewall hoặc internet")
except Exception as e:
    print(f"❌ LỖI KHÁC: {type(e).__name__}: {e}")