from fastapi import UploadFile
from hashlib import sha256

async def save_upload_file(file: UploadFile) -> str:
    # Saving to a local file is only temporary
    # consider object storage
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024)
            if not chunk:
                break
            buffer.write(chunk)

    file_hash = sha256(
        open(file_path, "rb").read()
    ).hexdigest()

    return file_hash
