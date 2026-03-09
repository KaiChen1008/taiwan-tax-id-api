# Taiwan Tax ID (UBN) Lookup API

This project provides a high-performance API to lookup Taiwan Unified Business Numbers (UBN/統一編號) by business name, with a ready-to-use Google Sheets integration.

---

## 🛠 Part 1: How to Start the Backend

The backend is a FastAPI service that processes a ~300MB government dataset. It automatically downloads the data on its first run.

### Local Run (Recommended for Dev)

1. **Install [uv](https://github.com/astral-sh/uv)** (Fastest Python package manager).
2. **Setup and Run:**
   ```bash
   # Install dependencies
   uv sync

   # Start the server
   make run
   ```

   The API will be available at `http://localhost:8092`.

### Docker Run

1. **Build and Start:**
   ```bash
   make up
   ```

   This runs the API in the background. Use `make down` to stop it.

> **Note:** The first startup takes 1-2 minutes because it needs to download and index the 300MB CSV file.

---

## 📊 Part 2: How to Use in Google Sheets

You can use this API directly inside Google Sheets to lookup thousands of company IDs at once.

### 1. Open the Script Editor

- Open your Google Sheet.
- Go to **Extensions** > **Apps Script**.

### 2. Add the Scripts

- Copy the content of [`frontend/formula.js`](frontend/formula.js) into a new file in the Apps Script editor.
- Copy the content of [`frontend/main.js`](frontend/main.js) into another file.
- **Important:** In both files, update the `url` variable to point to your deployed backend (e.g., `https://your-api-domain.com`).
- Click **Save** and name the project (e.g., "Tax ID Lookup").

### 3. Usage Methods

#### Method A: Custom Formula

In any cell, simply type:

```excel
=GET_TAX_ID("台灣積體電路製造股份有限公司")
```

It will return `23570644`.

#### Method B: Batch Lookup (Menu)

1. Refresh your Google Sheet. A new menu **🔍 Tax ID Lookup** will appear at the top.
2. Put all the company names you want to lookup in **Column A**.
3. Click **🔍 Tax ID Lookup** > **Start Lookup**.
4. The script will automatically fill **Column B** with the results.

---

## 🔌 API Reference

### Lookup Endpoint

`GET /get_ubn?name={NAME}`

**Request:**
`GET http://localhost:8092/get_ubn?name=台積電`

**Response:**

```json
["22099131"]
```

---

## 📂 Project Structure

- `app/`: FastAPI backend logic.
- `frontend/`: Google Apps Script source code.
- `data.csv`: Local data cache (gitignored).
- `GEMINI.md`: Detailed architecture and developer notes.

## 📄 License

MIT
