# Streamlit UI for Azure GenAI API

A user-friendly Streamlit interface for testing all Azure GenAI API endpoints locally.

## Features

- 💬 **Chat Interface**: Direct conversation with GPT-4o
- 🔍 **RAG Ask**: Query documents using Retrieval-Augmented Generation
- 📊 **Embedding Generator**: Create embeddings for text
- 🕸️ **GraphRAG**: Query knowledge graphs using Cosmos DB

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start FastAPI Server

In one terminal, start your FastAPI server:

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Start Streamlit App

In another terminal, start the Streamlit UI:

**Windows:**
```bash
run_streamlit.bat
```

**Linux/Mac:**
```bash
chmod +x run_streamlit.sh
./run_streamlit.sh
```

**Or directly:**
```bash
streamlit run streamlit_app.py
```

The Streamlit app will open in your browser at `http://localhost:8501`

## Configuration

### Change API URL

You can configure the API URL in two ways:

1. **In the UI**: Use the sidebar to change the API URL
2. **Environment Variable**: Set `API_URL` before running:
   ```bash
   export API_URL=http://your-api-url:8000
   streamlit run streamlit_app.py
   ```

### Testing Remote APIs

To test a deployed API (e.g., Azure App Service):

1. Set the API URL in the sidebar to your deployed endpoint
2. Example: `https://your-app.azurewebsites.net`

## Usage

### Chat Tab
- Enter your message in the text area
- Click "Send" to get a response from GPT-4o
- View chat history in the expandable section

### RAG Ask Tab
- Enter a question about your documents
- The system will search Azure AI Search and generate an answer
- View the JSON response for debugging

### Embed Tab
- Enter text to generate embeddings
- View embedding statistics and preview
- Download embeddings as JSON

### GraphAsk Tab
- Query your knowledge graph
- See which concepts were used in the answer
- View the full JSON response

## Troubleshooting

### Connection Issues

If you see connection errors:

1. **Check API is running**: Visit `http://localhost:8000/health` in your browser
2. **Check API URL**: Make sure the URL in the sidebar is correct
3. **Check CORS**: If testing remote APIs, ensure CORS is configured

### API Errors

- Check the JSON response in the expandable section
- Verify environment variables are set correctly
- Check FastAPI server logs for detailed error messages

## Features

- ✅ Real-time API testing
- ✅ Chat history
- ✅ JSON response viewer
- ✅ Connection testing
- ✅ Health check integration
- ✅ Download embeddings
- ✅ Responsive design

## Screenshots

The UI includes:
- Clean, modern interface
- Color-coded responses
- Expandable sections for details
- Sidebar configuration
- Direct links to API documentation

