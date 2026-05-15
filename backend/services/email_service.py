import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(to_email, otp, user_name=""):
    """Send OTP email to user."""
    try:
        mail_email    = current_app.config.get("MAIL_EMAIL")
        mail_password = current_app.config.get("MAIL_PASSWORD")

        if not mail_email or not mail_password:
            print("❌ Mail credentials not configured")
            return False

        # ── Build email ──
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{otp} is your PathPilot verification code"
        msg["From"]    = f"PathPilot <{mail_email}>"
        msg["To"]      = to_email

        html = f"""
        <div style="font-family:'DM Sans',Arial,sans-serif;max-width:480px;margin:0 auto;background:#0a0a0f;padding:40px 32px;border-radius:16px;border:1px solid rgba(255,255,255,0.08);">
            <div style="text-align:center;margin-bottom:32px;">
                <h1 style="color:#fff;font-size:24px;margin:0;">🚀 PathPilot</h1>
                <p style="color:rgba(255,255,255,0.4);font-size:13px;margin-top:6px;">Your Career Co-Pilot</p>
            </div>

            <p style="color:rgba(255,255,255,0.8);font-size:15px;">
                Hi {user_name or 'there'},
            </p>
            <p style="color:rgba(255,255,255,0.6);font-size:14px;line-height:1.6;">
                Use the code below to verify your email address. This code expires in <strong style="color:#fff;">10 minutes</strong>.
            </p>

            <div style="background:rgba(91,107,255,0.12);border:1px solid rgba(91,107,255,0.3);border-radius:12px;padding:28px;text-align:center;margin:28px 0;">
                <p style="color:rgba(255,255,255,0.5);font-size:12px;margin:0 0 8px 0;letter-spacing:2px;text-transform:uppercase;">Your OTP</p>
                <h2 style="color:#fff;font-size:42px;letter-spacing:12px;margin:0;font-weight:800;">{otp}</h2>
            </div>

            <p style="color:rgba(255,255,255,0.4);font-size:12px;line-height:1.6;">
                If you didn't create a PathPilot account, you can safely ignore this email.
            </p>

            <div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:32px;padding-top:20px;text-align:center;">
                <p style="color:rgba(255,255,255,0.25);font-size:11px;">© 2024 PathPilot. All rights reserved.</p>
            </div>
        </div>
        """

        msg.attach(MIMEText(html, "html"))

        # ── Send via Gmail SMTP ──
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(mail_email, mail_password)
            server.sendmail(mail_email, to_email, msg.as_string())

        print(f"✅ OTP email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        return False