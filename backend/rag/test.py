import io
from backend.rag.upload import upload_file_to_blob
from backend.rag.parser import pipeline

import io

async def main():
    with open("Document Print.pdf", "rb") as file:  # encoding 제거
        file_stream = io.BytesIO(file.read())
        file_name = "Document Print.pdf"
        
        # Upload the file to Azure Blob Storage
        blob_url = await upload_file_to_blob(file_stream, file_name)
        print(f"File uploaded to: {blob_url}")
        
        # Process the uploaded file
        result, err = await pipeline(blob_url)
        if err:
            print(f"Error processing file: {err}")
        else:
            for page in result:
                print(page)
    
    with open("result.txt", "w", encoding="utf-8") as result_file:  # 여기는 텍스트 모드니까 OK
        result_file.write(str(result))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    