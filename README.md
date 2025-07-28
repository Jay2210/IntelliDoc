# IntelliDoc

IntelliDoc is a document intelligence platform that allows users to upload, process, and interact with documents using AI-powered features. The project includes a Python backend for document processing and a Next.js frontend for user interaction.

## Features
- Upload documents (PDF, DOCX, etc.)
- Chunk and embed documents for semantic search
- Retrieve information using LLMs
- Store and manage documents with S3 and Pinecone
- Modern UI built with Next.js and Tailwind CSS

## Project Structure
```
app/            # Python backend modules
frontend/       # Next.js frontend
scripts/        # Utility scripts
data/           # Sample documents
requirements.txt# Python dependencies
```

## Getting Started

### Backend (Python)
1. Create a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run backend scripts as needed.

### Frontend (Next.js)
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the development server:
   ```sh
   npm run dev
   ```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
