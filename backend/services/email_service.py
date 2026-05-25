"""
Email Service - Gửi email quên mật khẩu
Dùng Gmail SMTP với App Password
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from config import Config

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def _build_reset_html(full_name: str, reset_url: str, expire_minutes: int) -> str:
        """Tạo nội dung email HTML đẹp theo theme văn học VN"""
        return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Đặt lại mật khẩu</title>
</head>
<body style="margin:0;padding:0;background:#f5f0e8;font-family: Arial, Helvetica, sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:#f5f0e8;padding:40px 20px;">
    <tr><td align="center">

      <!-- Card -->
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:16px;
                    box-shadow:0 8px 32px rgba(139,69,19,.15);
                    overflow:hidden;max-width:600px;">

        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#8B4513,#D2691E);
                     padding:40px 40px 32px;text-align:center;">
            <div style="font-size:3rem;margin-bottom:8px;">📖</div>
            <h1 style="margin:0;color:#ffffff;font-size:1.8rem;
                        letter-spacing:1px;text-shadow:1px 1px 3px rgba(0,0,0,.3);">
              Văn Học Việt Nam
            </h1>
            <p style="margin:6px 0 0;color:rgba(255,255,255,.85);font-size:.95rem;">
              Hệ thống tri thức văn học dân tộc
            </p>
          </td>
        </tr>

        <!-- Gold divider -->
        <tr>
          <td style="height:4px;
                     background:linear-gradient(90deg,#D4AF37,#F5D76E,#D4AF37);">
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:40px 40px 32px;">

            <h2 style="margin:0 0 16px;color:#3E2723;font-size:1.4rem;">
              Xin chào, {full_name}! 👋
            </h2>

            <p style="color:#555;line-height:1.7;margin:0 0 20px;font-size:1rem;">
              Chúng tôi nhận được yêu cầu <strong>đặt lại mật khẩu</strong>
              cho tài khoản của bạn trên hệ thống
              <strong style="color:#8B4513;">Văn Học Việt Nam</strong>.
            </p>

            <p style="color:#555;line-height:1.7;margin:0 0 28px;font-size:1rem;">
              Nhấn vào nút bên dưới để tạo mật khẩu mới.
              Link có hiệu lực trong <strong style="color:#D32F2F;">{expire_minutes} phút</strong>.
            </p>

            <!-- CTA Button -->
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td align="center" style="padding:8px 0 32px;">
                  <a href="{reset_url}"
                     style="display:inline-block;
                            background:linear-gradient(135deg,#8B4513,#D2691E);
                            color:#ffffff;
                            text-decoration:none;
                            padding:16px 40px;
                            border-radius:50px;
                            font-size:1.05rem;
                            font-weight:bold;
                            letter-spacing:.5px;
                            box-shadow:0 4px 16px rgba(139,69,19,.4);">
                    🔑 Đặt lại mật khẩu
                  </a>
                </td>
              </tr>
            </table>

            <!-- Warning box -->
            <div style="background:#FFF8E1;border:1px solid #D4AF37;
                        border-radius:10px;padding:16px 20px;margin-bottom:24px;">
              <p style="margin:0;color:#6D4C41;font-size:.9rem;line-height:1.6;">
                ⚠️ <strong>Lưu ý bảo mật:</strong><br>
                • Nếu bạn <strong>không</strong> yêu cầu đặt lại mật khẩu,
                  hãy bỏ qua email này.<br>
                • Link chỉ sử dụng được <strong>1 lần</strong>
                  và hết hạn sau <strong>{expire_minutes} phút</strong>.<br>
                • Không chia sẻ link này với bất kỳ ai.
              </p>
            </div>

            <!-- Fallback link -->
            <p style="color:#999;font-size:.82rem;line-height:1.5;
                       border-top:1px solid #f0f0f0;padding-top:16px;margin:0;">
              Nếu nút không hoạt động, copy và dán link sau vào trình duyệt:<br>
              <a href="{reset_url}"
                 style="color:#8B4513;word-break:break-all;">{reset_url}</a>
            </p>

          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#3E2723;padding:24px 40px;text-align:center;">
            <p style="margin:0;color:rgba(255,255,255,.7);font-size:.85rem;">
              © 2026 Văn Học Việt Nam — Đồ án tốt nghiệp
            </p>
            <p style="margin:6px 0 0;color:rgba(255,255,255,.5);font-size:.8rem;">
              Email này được gửi tự động, vui lòng không trả lời.
            </p>
          </td>
        </tr>

      </table>
      <!-- End card -->

    </td></tr>
  </table>

</body>
</html>
"""

    @staticmethod
    def send_reset_password(to_email: str, full_name: str, reset_token: str) -> bool:
        """
        Gửi email đặt lại mật khẩu
        Returns True nếu gửi thành công
        """
        try:
            reset_url      = f"{Config.APP_URL}/reset-password?token={reset_token}"
            expire_minutes = Config.RESET_TOKEN_EXPIRE_MINUTES

            # Build message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = '🔑 Đặt lại mật khẩu - Văn Học Việt Nam'
            msg['From']    = Config.MAIL_FROM or Config.MAIL_USERNAME
            msg['To']      = to_email

            # Plain text fallback
            plain = (
                f"Xin chào {full_name},\n\n"
                f"Nhấn vào link sau để đặt lại mật khẩu "
                f"(hết hạn sau {expire_minutes} phút):\n\n"
                f"{reset_url}\n\n"
                f"Nếu bạn không yêu cầu, hãy bỏ qua email này.\n\n"
                f"Văn Học Việt Nam"
            )
            msg.attach(MIMEText(plain, 'plain', 'utf-8'))

            # HTML content
            html = EmailService._build_reset_html(full_name, reset_url, expire_minutes)
            msg.attach(MIMEText(html, 'html', 'utf-8'))

            # Send via SMTP
            with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                server.ehlo()
                if Config.MAIL_USE_TLS:
                    server.starttls()
                    server.ehlo()
                server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                server.sendmail(
                    Config.MAIL_USERNAME,
                    to_email,
                    msg.as_string()
                )

            logger.info(f"✅ Đã gửi email đặt lại MK đến {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("❌ SMTP Auth thất bại — kiểm tra MAIL_USERNAME/MAIL_PASSWORD")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP lỗi: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Lỗi gửi email: {e}", exc_info=True)
            return False