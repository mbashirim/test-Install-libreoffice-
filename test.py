
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio
from pptx import Presentation
import tempfile
import boto3
from botocore.exceptions import NoCredentialsError
import subprocess

# Environment variables
# TOKEN = os.environ.get('TOKEN')
TOKEN = ""
LIARA_ENDPOINT_URL = "https://storage.c2.liara.space"
LIARA_ACCESS_KEY = "3mmsl1rs77o3qm0p"
LIARA_SECRET_KEY = "3d754b42-3238-4836-9443-e4442fd9749e"
BUCKET_NAME = "pedantic-mendel-n4-aiorwn"

if not TOKEN:
    raise ValueError("Please set TOKEN environment variable")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def convert_pptx_to_pdf(input_path, output_path):
    
        return True


def get_s3_client():
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=LIARA_ENDPOINT_URL,
            aws_access_key_id=LIARA_ACCESS_KEY,
            aws_secret_access_key=LIARA_SECRET_KEY
        )
        return s3_client
    except NoCredentialsError:
        print("Credentials not available.")
        return None

def upload_to_s3(file_path, file_name):
    s3_client = get_s3_client()
    if s3_client:
        try:
            with open(file_path, 'rb') as file:
                s3_client.upload_fileobj(file, BUCKET_NAME, file_name)
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    return False

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("برای من فایل پاور پوینت بفرستید تا تحلیل کنم")

@dp.message(lambda message: message.document and message.document.file_name.endswith(('.pptx', '.ppt')))
async def handle_ppt(message: types.Message):
    try:
        # Download PowerPoint file
        with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as ppt_file:
            await bot.download(message.document.file_id, destination=ppt_file.name)
            
            # Create PDF file path
            pdf_path = ppt_file.name.replace('.pptx', '.pdf')
            
            # Convert to PDF
            convert_pptx_to_pdf(ppt_file.name, pdf_path)
            
            # Upload PDF to S3
            pdf_filename = message.document.file_name.replace('.pptx', '.pdf')
            upload_success = upload_to_s3(ppt_file.name, pdf_filename)
            
            # Analyze PowerPoint
            prs = Presentation(ppt_file.name)
            slide_count = len(prs.slides)
            
            # Create response message
            status_msg = "فایل PDF با موفقیت در Storage آپلود شد." if upload_success else "خطا در آپلود فایل PDF"
            
            # Create inline keyboard
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(
                        text="Open Web",
                        web_app=types.WebAppInfo(url="https://www.google.com")
                    )]
                ]
            )
            
            # Send PDF file to user
            with open(ppt_file.name, 'rb') as pdf_file:
                await message.answer_document(
                    types.BufferedInputFile(
                        pdf_file.read(),
                        filename=pdf_filename
                    )
                )

            # Send status message
            await message.answer(
                f"نام فایل: {message.document.file_name}\n"
                f"تعداد اسلایدها: {slide_count}\n"
                f"وضعیت آپلود: {status_msg}",
                reply_markup=keyboard
            )
            
            # Clean up
            os.unlink(ppt_file.name)
            os.unlink(pdf_path)
            
    except Exception as e:
        await message.answer(f"خطا در پردازش فایل: {str(e)}")

@dp.message()
async def echo(message: types.Message):
    await message.answer("لطفا یک فایل پاورپوینت ارسال کنید.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
