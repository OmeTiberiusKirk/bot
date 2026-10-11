import asyncio
import os
import random
from playwright.async_api import async_playwright
from pathlib import Path
from faker import Faker
from dotenv import load_dotenv

load_dotenv()

# ตั้งค่าเบอร์โทรศัพท์เริ่มต้น
startPhoneNumber = 611420000
startBankAccountNumber = 503091000
prefix = "0"
total_runs = 100000


async def run_bot():
    url = os.getenv("URL_1")
    fake = Faker('th_TH')
    Path("phone_number.txt").touch(exist_ok=True)
    print(f"URL: {url}")

    async with async_playwright() as p:
        for i in range(total_runs):
            currentPhone = f"{prefix}{startPhoneNumber + i}"
            currentBankAccount = f"{prefix}{startBankAccountNumber + i}"
            print(f"\n--- รอบที่ {i+1} | เบอร์: {currentPhone} ---")

            # ตั้งค่า Browser พร้อม Proxy (ถ้าไม่ใช้ Proxy ให้ลบพารามิเตอร์ proxy ออกได้)
            browser = await p.chromium.launch(
                headless=True,  # เปลี่ยนเป็น True ถ้าไม่อยากเปิดเบราว์เซอร์
                # proxy={"server": "http://username:password@proxy_address:port"}
            )

            context = await browser.new_context()
            page = await context.new_page()

            # ดักจับ Network Event เพื่อดู HTTP Status Code
            def handle_response(response):
                if response.status >= 400:
                    print(f"[Network Log] URL: {response.url} | Status: {response.status}")
                    with open("phone_number.txt", "a") as f:
                        f.write(currentPhone + '\n')

            page.on("response", handle_response)

            try:
                # เปิดหน้าเว็บ ( Playwright มี auto-wait รอหน้าเว็บโหลดเสร็จในตัว)
                response = await page.goto(url)
                print(f"Main Page Status Code: {response.status}")

                await page.fill(".step-2 input[aria-describedby='form-phone']", currentPhone)
                await page.click(".step-2 button")
                await page.click(".swal2-confirm")

                await page.fill(".step-3 #Password", 'P@ssw0rd11007')
                await page.select_option(".step-3 .form-group:nth-of-type(3) select", random.choice(['1', '2', '4', '5', '8']))
                await page.click(".step-3 .form-group:nth-of-type(4) .v-select")
                await page.wait_for_timeout(1000)
                await page.click(f".step-3 .form-group:nth-of-type(4) ul#vs1__listbox li:nth-of-type({random.randint(1, 11)})")
                await page.fill(".step-3 .form-group:nth-of-type(5) input", currentBankAccount)

                inputs = await page.locator(".step-3 > div:nth-last-of-type(2) input").all()
                for input, value in zip(inputs, [fake.first_name(), fake.last_name()]):
                    await input.fill(value)

                await page.click(".step-3 > div:last-child button")
                await page.wait_for_timeout(1000 * 10)
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในรอบที่ {i+1}: {e}")

            finally:
                await context.close()
                await browser.close()

# รันฟังก์ชัน Async
if __name__ == "__main__":
    asyncio.run(run_bot())
