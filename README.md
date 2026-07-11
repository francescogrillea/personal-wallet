# Personal Wallet API

## Description

**Personal Wallet** is a REST API that allows you to extract bank transactions from bank statements and save them automatically to a Google Sheet. The application is designed to handle standardized bank export flows, parse the data, and archive it in a structured manner.

The flow is simple:
1. Upload a bank statement file
2. The API identifies the bank provider by the file name
3. Extracts and validates the transactions
4. Saves data to the configured backend 

## Providers
**Storage**:
* Google Sheets

**Banks**:
* Fineco - .xlsx format

---

## Starting the Server

### Prerequisites
- Python 3.12 or higher
- `uv` package manager installed

### Installing Dependencies
```bash
uv sync
```

### Starting the API
```bash
uv run main.py
```

The server will start on:
```
http://localhost:8000
```

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

---

## Configuration

The application uses a configuration file `config/config.yaml` to set up services:

```yaml
storage_service:
  provider: google_sheets
  config:
    spreadsheet_id: YOUR_SPREADSHEET_ID
    range_name: Sheet1!A1

parsing_service:
  provider: your_provider_here
  config:
    placeholder: value
```

### Environment Variables

For Google Sheets, configure the credentials:
```bash
GOOGLE_SHEET_TYPE=service_account
GOOGLE_SHEET_PROJECT_ID=your_project_id
GOOGLE_SHEET_PRIVATE_KEY_ID=your_private_key_id
GOOGLE_SHEET_PRIVATE_KEY="your_private_key"
GOOGLE_SHEET_CLIENT_EMAIL=your_email@project.iam.gserviceaccount.com
GOOGLE_SHEET_CLIENT_ID=your_client_id
GOOGLE_SHEET_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_SHEET_TOKEN_URI=https://oauth2.googleapis.com/token
```

---

## API Endpoints

### 1. GET /health
Checks the health status of the service.

**cURL:**
```bash
curl -X GET http://localhost:8000/health
```

**Postman:**
- **Method**: GET
- **URL**: `http://localhost:8000/health`

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

---

### 2. GET /help
Gets detailed information about the API and its endpoints.

**cURL:**
```bash
curl -X GET http://localhost:8000/help
```

**Postman:**
- **Method**: GET
- **URL**: `http://localhost:8000/help`

**Response (200 OK):**
```json
{
  "description": "Personal Wallet is a REST API for parsing and managing personal bank transaction exports...",
  "endpoints": {
    "GET /health": "Returns the service health status.",
    "GET /help": "Returns this help message.",
    "POST /upload": "Upload a bank movements file. Returns a list of parsed transactions."
  }
}
```

---

### 3. POST /upload
Upload a bank statement file and save the transactions.

**cURL:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@/path/to/your_bank_export"
```

**Postman:**
- **Method**: POST
- **URL**: `http://localhost:8000/upload`
- **Body**:
  - Select **form-data**
  - Add a **File** type field with key `file`
  - Select the file to upload
- **Click**: Send

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "15 transactions saved successfully",
  "transactions": [
    {
      "uid": "123e4567-e89b-12d3-a456-426614174000",
      "value_date": "2025-01-16",
      "accounting_date": "2025-01-15",
      "amount": 1000.00,
      "description": "Bonifico ricevuto - Bonifico ricevuto da Azienda XYZ",
      "category": null,
      "notes": null,
      "upload_datetime": "2025-01-11T10:30:45.123456",
      "digest": "abc123def456..."
    }
  ]
}
```
