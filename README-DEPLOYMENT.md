# Deployment Guide for Docling API

## Quick Start for Coolify

This fork adds simple API key authentication and is optimized for Coolify deployment.

### Features Added
- Simple API key authentication via `X-API-Key` header
- Simplified `/convert` endpoint that returns plain Markdown
- Raw body endpoint `/convert/raw` for direct document uploads
- Coolify-ready Docker configuration

### API Endpoints

#### 1. Convert Document to Markdown
```bash
POST /convert
Headers:
  X-API-Key: your-api-key (if configured)
Body:
  file: (multipart form data)
Response: Plain Markdown text
```

#### 2. Convert Raw Document
```bash
POST /convert/raw  
Headers:
  X-API-Key: your-api-key (if configured)
  Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
  Filename: document.docx (optional)
Body: Raw document bytes
Response: Plain Markdown text
```

### Deployment on Coolify

1. **In Coolify:**
   - Create new application
   - Choose "Docker Compose" 
   - Set repository: `https://github.com/theinventor/docling-api.git`
   - Set Docker Compose file: `docker-compose.coolify.yml`

2. **Set Environment Variables in Coolify:**
   ```
   API_KEY=your-secure-api-key-here
   PORT=8000
   ```

3. **Deploy!**

### Local Testing

1. Copy environment file:
   ```bash
   cp .env.example .env
   # Edit .env to set your API_KEY
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose -f docker-compose.coolify.yml up
   ```

3. Test the API:
   ```bash
   curl -X POST http://localhost:8000/convert \
     -H "X-API-Key: your-api-key" \
     -F "file=@document.docx"
   ```

### Security Notes
- Always set a strong API_KEY in production
- The API_KEY should be at least 32 characters
- Never commit .env files to the repository
- Use Coolify's environment variables for secrets

### Supported Formats
- DOCX, PDF, PPTX
- HTML, Markdown, AsciiDoc  
- Images (PNG, JPG, TIFF, BMP)
- CSV files