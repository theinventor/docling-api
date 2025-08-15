import os
from io import BytesIO
from fastapi import FastAPI, File, HTTPException, UploadFile, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from typing import Optional

from document_converter.service import DocumentConverterService, DoclingDocumentConversion
from document_converter.utils import is_file_format_supported

app = FastAPI(title="Docling API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Initialize converter
converter = DoclingDocumentConversion()
document_converter_service = DocumentConverterService(document_converter=converter)

# API Key from environment
API_KEY = os.environ.get("API_KEY", "your-secret-api-key-here")


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from header"""
    if not API_KEY or API_KEY == "your-secret-api-key-here":
        # No authentication if API_KEY not set
        return True
    
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return True


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "docling-api"}


@app.post("/convert", response_class=PlainTextResponse)
async def convert_document_to_markdown(
    file: UploadFile = File(...),
    mimetype: Optional[str] = Header(None),
    filename: Optional[str] = Header(None),
    authorized: bool = Depends(verify_api_key)
):
    """
    Convert a document to Markdown format.
    
    - Accepts: DOCX, PDF, PPTX, HTML, Images, etc.
    - Returns: Plain Markdown text
    - Authentication: X-API-Key header (if API_KEY env is set)
    """
    try:
        # Read file content
        file_bytes = await file.read()
        
        # Use provided filename or fall back to uploaded filename
        doc_filename = filename or file.filename
        
        # Check if file format is supported
        if not is_file_format_supported(file_bytes, doc_filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {doc_filename}"
            )
        
        # Convert document
        result = document_converter_service.convert_document(
            (doc_filename, BytesIO(file_bytes)),
            extract_tables=False,
            image_resolution_scale=4,
        )
        
        # Return markdown content
        if result and hasattr(result, 'markdown'):
            return PlainTextResponse(content=result.markdown, media_type="text/markdown")
        else:
            raise HTTPException(
                status_code=500,
                detail="Conversion failed - no markdown output"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion error: {str(e)}"
        )


@app.post("/convert/raw", response_class=PlainTextResponse)
async def convert_raw_document_to_markdown(
    body: bytes,
    content_type: Optional[str] = Header(None),
    filename: Optional[str] = Header(None),
    authorized: bool = Depends(verify_api_key)
):
    """
    Convert a raw document (sent as body) to Markdown format.
    
    - Send document as raw body
    - Specify Content-Type and Filename headers
    - Returns: Plain Markdown text
    - Authentication: X-API-Key header (if API_KEY env is set)
    """
    try:
        # Use filename from header or generate one based on content type
        if not filename:
            ext_map = {
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document.docx",
                "application/pdf": "document.pdf",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": "presentation.pptx",
                "text/html": "document.html",
                "image/png": "image.png",
                "image/jpeg": "image.jpg",
            }
            filename = ext_map.get(content_type, "document")
        
        # Check if file format is supported
        if not is_file_format_supported(body, filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {filename}"
            )
        
        # Convert document
        result = document_converter_service.convert_document(
            (filename, BytesIO(body)),
            extract_tables=False,
            image_resolution_scale=4,
        )
        
        # Return markdown content
        if result and hasattr(result, 'markdown'):
            return PlainTextResponse(content=result.markdown, media_type="text/markdown")
        else:
            raise HTTPException(
                status_code=500,
                detail="Conversion failed - no markdown output"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)