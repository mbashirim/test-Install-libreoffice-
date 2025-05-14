import subprocess

def check_libreoffice():
    try:
        # اجرای دستور libreoffice برای تست نصب بودن
        result = subprocess.run(["libreoffice", "--version"], check=True, text=True, capture_output=True)
        print("LibreOffice Version:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("LibreOffice not installed or not accessible.")
        print(e)
    except Exception as e:
        print("Unexpected error:", e)

if __name__ == "__main__":
    check_libreoffice()
