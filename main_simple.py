import os
from io import BytesIO
from fastapi import FastAPI, File, HTTPException, UploadFile, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from typing import Optional
from docling.document_converter import DocumentConverter

app = FastAPI(title="Docling API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Initialize Docling converter directly
converter = DocumentConverter()

# API Key from environment
API_KEY = os.environ.get("API_KEY", "")


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from header"""
    if not API_KEY:
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
    return {"status": "healthy", "service": "docling-api", "redis": "not-required"}


@app.post("/convert", response_class=PlainTextResponse)
async def convert_document_to_markdown(
    file: UploadFile = File(...),
    authorized: bool = Depends(verify_api_key)
):
    """
    Convert a document to Markdown format.
    
    - Accepts: DOCX, PDF, PPTX, HTML, Images, etc.
    - Returns: Plain Markdown text
    - Authentication: X-API-Key header (if API_KEY env is set)
    """
    try:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Convert using Docling
            result = converter.convert(tmp_path)
            
            # Get markdown content
            markdown_content = result.document.export_to_markdown()
            
            return PlainTextResponse(
                content=markdown_content, 
                media_type="text/markdown"
            )
        finally:
            # Clean up temp file
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion error: {str(e)}"
        )


@app.post("/convert/raw", response_class=PlainTextResponse)
async def convert_raw_document_to_markdown(
    request: Request,
    content_type: Optional[str] = Header(None),
    x_filename: Optional[str] = Header(None),
    authorized: bool = Depends(verify_api_key)
):
    """
    Convert a raw document (sent as body) to Markdown format.
    
    - Send document as raw body
    - Specify X-Filename header for the filename
    - Returns: Plain Markdown text
    - Authentication: X-API-Key header (if API_KEY env is set)
    """
    try:
        # Get raw body
        body = await request.body()
        
        # Determine filename
        if not x_filename:
            ext_map = {
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
                "application/pdf": ".pdf",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
                "text/html": ".html",
                "image/png": ".png",
                "image/jpeg": ".jpg",
            }
            ext = ext_map.get(content_type, "")
            x_filename = f"document{ext}"
        
        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{x_filename}") as tmp_file:
            tmp_file.write(body)
            tmp_path = tmp_file.name
        
        try:
            # Convert using Docling
            result = converter.convert(tmp_path)
            
            # Get markdown content
            markdown_content = result.document.export_to_markdown()
            
            return PlainTextResponse(
                content=markdown_content,
                media_type="text/markdown"
            )
        finally:
            # Clean up temp file
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)