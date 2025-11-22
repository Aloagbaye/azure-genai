"""
Streamlit UI for testing Azure GenAI API endpoints
"""
import streamlit as st
import requests
import json
import os
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="Azure GenAI API Tester",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .endpoint-section {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_url' not in st.session_state:
    st.session_state.api_url = os.getenv('API_URL', 'http://localhost:8000')
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def call_api(endpoint: str, payload: dict) -> Optional[dict]:
    """Make API call and return response"""
    try:
        url = f"{st.session_state.api_url}{endpoint}"
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                st.json(error_detail)
            except:
                st.text(e.response.text)
        return None

def main():
    # Header
    st.markdown('<div class="main-header">🤖 Azure GenAI API Tester</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_url = st.text_input(
            "API URL",
            value=st.session_state.api_url,
            help="Base URL of your FastAPI server"
        )
        st.session_state.api_url = api_url.rstrip('/')
        
        # Test connection
        if st.button("🔌 Test Connection"):
            try:
                response = requests.get(f"{st.session_state.api_url}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Connected!")
                    st.json(response.json())
                else:
                    st.warning(f"⚠️ Server responded with status {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
        
        st.divider()
        
        # API Documentation link
        st.markdown(f"""
        ### 📚 API Docs
        [OpenAPI Docs]({st.session_state.api_url}/docs)
        
        [ReDoc]({st.session_state.api_url}/redoc)
        """)
        
        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🔍 RAG Ask", "📊 Embed", "🕸️ GraphAsk"])
    
    # Tab 1: Chat
    with tab1:
        st.header("💬 Chat with GPT-4o")
        st.markdown("Direct conversation with Azure OpenAI GPT-4o model")
        
        # Chat interface
        user_input = st.text_area(
            "Enter your message:",
            height=100,
            placeholder="Ask me anything..."
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            send_button = st.button("Send", type="primary", use_container_width=True)
        
        if send_button and user_input:
            with st.spinner("Thinking..."):
                result = call_api("/chat", {"user_input": user_input})
                
                if result:
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        response = result.get("response", "")
                        
                        # Display in chat format
                        st.markdown("### Your Message:")
                        st.info(user_input)
                        
                        st.markdown("### Assistant Response:")
                        st.success(response)
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "user": user_input,
                            "assistant": response
                        })
                        
                        # Show JSON response
                        with st.expander("📋 View JSON Response"):
                            st.json(result)
        
        # Chat history
        if st.session_state.chat_history:
            st.divider()
            st.subheader("💭 Chat History")
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
                with st.expander(f"Conversation {len(st.session_state.chat_history) - i + 1}"):
                    st.markdown(f"**You:** {chat['user']}")
                    st.markdown(f"**Assistant:** {chat['assistant']}")
    
    # Tab 2: RAG Ask
    with tab2:
        st.header("🔍 RAG-Powered Q&A")
        st.markdown("Ask questions using Retrieval-Augmented Generation (RAG) with Azure AI Search")
        
        query = st.text_area(
            "Enter your question:",
            height=100,
            placeholder="What information are you looking for?"
        )
        
        if st.button("🔍 Search & Answer", type="primary"):
            if query:
                with st.spinner("Searching documents and generating answer..."):
                    result = call_api("/ask", {"query": query})
                    
                    if result:
                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            response = result.get("response", "")
                            
                            st.markdown("### 📝 Answer:")
                            st.success(response)
                            
                            # Show JSON response
                            with st.expander("📋 View JSON Response"):
                                st.json(result)
            else:
                st.warning("Please enter a question")
    
    # Tab 3: Embed
    with tab3:
        st.header("📊 Text Embedding")
        st.markdown("Generate embeddings for text using Azure OpenAI")
        
        text_to_embed = st.text_area(
            "Enter text to embed:",
            height=150,
            placeholder="Enter the text you want to convert to an embedding vector..."
        )
        
        if st.button("📊 Generate Embedding", type="primary"):
            if text_to_embed:
                with st.spinner("Generating embedding..."):
                    result = call_api("/embed", {"text": text_to_embed})
                    
                    if result:
                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            embedding = result.get("embedding", [])
                            
                            st.markdown("### 📊 Embedding Vector:")
                            
                            # Show statistics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Dimensions", len(embedding))
                            with col2:
                                st.metric("Min Value", f"{min(embedding):.4f}")
                            with col3:
                                st.metric("Max Value", f"{max(embedding):.4f}")
                            
                            # Show preview
                            st.markdown("#### Preview (first 10 dimensions):")
                            st.code(f"[{', '.join([f'{x:.4f}' for x in embedding[:10]])}, ...]")
                            
                            # Show full embedding in expander
                            with st.expander("📋 View Full Embedding Vector"):
                                st.json(embedding)
                            
                            # Download option
                            embedding_json = json.dumps(embedding)
                            st.download_button(
                                label="📥 Download Embedding (JSON)",
                                data=embedding_json,
                                file_name="embedding.json",
                                mime="application/json"
                            )
            else:
                st.warning("Please enter text to embed")
    
    # Tab 4: GraphAsk
    with tab4:
        st.header("🕸️ GraphRAG Query")
        st.markdown("Query using graph knowledge base with Cosmos DB Gremlin")
        
        graph_query = st.text_area(
            "Enter your query:",
            height=100,
            placeholder="Ask a question that will be answered using graph relationships..."
        )
        
        if st.button("🕸️ Query Graph", type="primary"):
            if graph_query:
                with st.spinner("Querying graph and generating answer..."):
                    result = call_api("/graphask", {"query": graph_query})
                    
                    if result:
                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            response = result.get("response", "")
                            concepts = result.get("concepts_used", [])
                            
                            st.markdown("### 🎯 Answer:")
                            st.success(response)
                            
                            if concepts:
                                st.markdown("### 🔗 Concepts Used:")
                                st.info(", ".join(concepts))
                            
                            # Show JSON response
                            with st.expander("📋 View JSON Response"):
                                st.json(result)
            else:
                st.warning("Please enter a query")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Azure GenAI API Tester | Built with Streamlit</p>
        <p>API Status: <a href="{}/health" target="_blank">Health Check</a></p>
    </div>
    """.format(st.session_state.api_url), unsafe_allow_html=True)

if __name__ == "__main__":
    main()

