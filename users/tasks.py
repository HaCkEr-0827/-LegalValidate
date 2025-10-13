from celery import shared_task

@shared_task
def send_otp_via_console(to, code):
    print(f"[OTP] Sending OTP to {to}: {code}")

@shared_task
def send_otp_via_email(email, code):
    # console'ga chiqarish (real email yubormaydi)
    print(f"[OTP Email] To: {email}, Code: {code}")
