# ResumeTailor-API

ResumeTailor-API is an intelligent resume tailoring API that leverages Large Language Models (LLMs) to automatically adapt your resume for specific job applications. Built as a RESTful web service, it extracts job requirements from job descriptions, tailors your resume content to match, and generates professional cover letters, all while maintaining accuracy and relevance.

## ✨ Features

### 🎯 Intelligent Job Analysis

- **Job Profile Extraction**: Automatically parses job descriptions to extract key requirements, technical skills, and role expectations
- **Multi-stage Review**: Interactive editing and refinement of extracted job profiles for accuracy

### 📝 Resume Tailoring

- **Smart Adaptation**: Tailors your resume content to highlight relevant experience for specific positions
- **Section-wise Editing**: Edit individual resume sections with AI assistance
- **Job-specific Focus**: Emphasizes skills and experiences that match job requirements

### 💌 Cover Letter Generation

- **Contextual Generation**: Creates personalized cover letters based on your resume and job requirements
- **Style Matching**: Analyzes job description tone and matches writing style
- **Interactive Refinement**: Edit and improve generated cover letters with AI assistance

### 🖥️ Web Interface

- **FastAPI Web API**: RESTful API for integration with web frontends and automation

### 📄 Professional Output

- **Multiple Formats**: Generates HTML and PDF versions of resumes and cover letters
- **Professional Templates**: Uses high-quality templates via ResumeGen microservice
- **Session Management**: Maintains application state throughout the tailoring process

## 🏗️ Architecture

ResumeTailor follows a microservices architecture:

- **ResumeTailor API**: Main application service (FastAPI)
- **ResumeGen API**: Document generation service (Node.js + Express)
- **PDF Service**: PDF rendering service (Puppeteer)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Docker Deployment

1. **Clone the repository**:

   ```bash
   git clone <your-repo-url>
   cd ResumeTailor-cli
   ```

2. **Configure environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

3. **Set up your resume data**:

   ```bash
   # Copy example resume (contains sample data)
   cp data/full_resume.yaml.example data/full_resume.yaml
   ```

   **Note**: This copies the resume with example data from Alex Smith. See the Configuration section below to set up your own resume data.

4. **Start all services**:

   ```bash
   docker-compose up --build
   ```

5. **Access the application**:
   - API: http://localhost:8080
   - Health check: http://localhost:8080/health
   - API documentation: http://localhost:8080/docs

## ⚙️ Configuration

### Resume Data Setup

To use ResumeTailor with your own resume data:

1. **Copy the empty template**:

   ```bash
   cp data/full_resume.yaml.empty data/full_resume.yaml
   ```

2. **Fill in your information**: Edit `data/full_resume.yaml` following the structure and comments in the file. The comments provide detailed guidance on:

   - Required vs optional fields
   - Expected data formats
   - Tips for maximizing AI effectiveness

3. **Personal information file**: The `data/private_info.json` file does not need to be filled - it's optional and can be used for additional personal data if needed.

**Note**: The more complete and detailed your resume data, the better the AI can tailor it for specific job applications. Don't worry about making it sound perfect - include all relevant experience, skills, and achievements in simple terms.

### Environment Variables

ResumeTailor can be configured using environment variables. Copy the example file and customize as needed:

```bash
cp .env.example .env
```

#### Required Configuration

- **`OPENAI_API_KEY`**: Your OpenAI API key for GPT model access (required)

#### Optional Configuration

**File Paths:**

- **`OUTPUT_DIR`**: Directory for generated files (default: "output")
- **`DATA_DIR`**: Directory containing resume data files (default: "data")

**LLM Models:**

- **`LLM_MODEL_SUMMARY`**: Model for job description summarization (default: "gpt-4o-mini")
- **`LLM_MODEL_RESUME`**: Model for resume generation (default: "gpt-4o-mini")
- **`LLM_MODEL_COVER_LETTER`**: Model for cover letter generation (default: "gpt-4o-mini")
- **`LLM_MODEL_GRADING`**: Model for content evaluation (default: "gpt-4o-mini")

**Development/Testing:**

- **`LANGSMITH_TRACING`**: Enable LangSmith tracing for debugging (default: false)
- **`LANGSMITH_ENDPOINT`**: LangSmith API endpoint URL
- **`LANGSMITH_API_KEY`**: LangSmith API key for tracing
- **`LANGSMITH_PROJECT`**: LangSmith project name for organizing traces

**Note**: You can use different models for different tasks. For production use, consider `gpt-4o` for higher quality output, or stick with `gpt-4o-mini` for cost efficiency.

## 📖 Usage

### API Interface

#### 1. Initialize a Session

```bash
curl -X POST "http://localhost:8080/application/initialize" \
  -H "Content-Type: application/json" \
  -d '{
    "application_type": "job_application",
    "steps": ["job_profile", "resume", "cover_letter"]
  }'
```

#### 2. Extract Job Profile

```bash
curl -X POST "http://localhost:8080/job-profile/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "job_description": "Your job description text here..."
  }'
```

#### 3. Generate Tailored Resume

```bash
curl -X POST "http://localhost:8080/resume/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id"
  }'
```

#### 4. Generate Cover Letter

```bash
curl -X POST "http://localhost:8080/cover-letter/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id"
  }'
```

#### 5. Complete Application

```bash
curl -X POST "http://localhost:8080/application/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "action": "save"
  }'
```

### Postman Collection

A complete Postman collection is included in the repository (`AutoApplyBackendAPI.postman_collection.json`) to help you test and explore the API endpoints interactively.

#### Importing the Collection

1. **Open Postman** and click "Import" in the top toolbar
2. **Select the file** `AutoApplyBackendAPI.postman_collection.json` from the repository root
3. **Import the collection** - it will appear in your collections sidebar

#### Using the Collection

The collection includes pre-configured requests for all API endpoints:

- **Application Management**: Initialize and complete application sessions
- **Job Profile Operations**: Extract and edit job profiles from descriptions
- **Resume Generation**: Generate and edit tailored resumes
- **Cover Letter Creation**: Generate and edit personalized cover letters
- **Data Access**: Retrieve application history and download generated documents

#### Variables and Configuration

1. **Set up environment variables** in Postman:

   - `{{session_id}}`: Session ID returned from the initialize endpoint
   - `{{job_description}}`: Job description text for profile extraction
   - Base URL is pre-configured as `http://localhost:8080`

#### Workflow Example

1. **Initialize Session**: Use "Application - Initialize" to create a new session
2. **Copy Session ID**: From the response, copy the session_id and set it as a Postman variable
3. **Set Job Description**: Set the `{{job_description}}` variable with your job posting text
4. **Extract Job Profile**:
   - Use "Job Profile - Extract" (variables will be used automatically)
   - Edit job profile with "Job Profile - Edit"
   - Finalize job profile with "Job Profile - Complete"
5. **Generate Resume**:
   - Use "Resume - Generate" with the session ID
   - Edit sections as needed using "Resume - Edit Section"
   - Complete the resume with "Resume - Complete"
6. **Generate Cover Letter**:
   - Use "Cover Letter - Generate" with the session ID
   - Edit cover letter using "Cover Letter - Edit"
   - Complete the cover letter with "Cover Letter - Complete"
7. **Complete Application**: Use "Application - Complete" to finalize and save
8. **Access Results**: Set `{{id}}` variable and use data endpoints to view/download documents

### API Endpoints

#### Health Checks

All services include health checks:

- **ResumeTailor API**: `curl http://localhost:8080/health`
- **ResumeGen API**: HTTP endpoint monitoring
- **PDF Service**: Process health monitoring

| Endpoint                         | Method | Description                            |
| -------------------------------- | ------ | -------------------------------------- |
| `/health`                        | GET    | Health check                           |
| `/application/initialize`        | POST   | Create new session                     |
| `/application/complete`          | POST   | Finalize and save application          |
| `/job-profile/generate`          | POST   | Extract job profile from description   |
| `/job-profile/edit`              | POST   | Edit job profile with suggestions      |
| `/job-profile/complete`          | POST   | Finalize job profile                   |
| `/resume/generate`               | POST   | Generate tailored resume               |
| `/resume/edit-section`           | POST   | Edit specific resume section           |
| `/resume/complete`               | POST   | Finalize resume                        |
| `/cover-letter/generate`         | POST   | Generate cover letter                  |
| `/cover-letter/edit`             | POST   | Edit cover letter                      |
| `/cover-letter/complete`         | POST   | Finalize cover letter                  |
| `/data/full_resume.json`         | GET    | Get your complete resume data          |
| `/data/history`                  | GET    | List all saved applications            |
| `/data/{id}/job_description.txt` | GET    | Download job description text file     |
| `/data/{id}/job_profile.json`    | GET    | Get job profile JSON for application   |
| `/data/{id}/resume.html`         | GET    | View resume HTML for application       |
| `/data/{id}/cover_letter.html`   | GET    | View cover letter HTML for application |
| `/data/{id}/resume.pdf`          | GET    | Download resume PDF                    |
| `/data/{id}/cover_letter.pdf`    | GET    | Download cover letter PDF              |
| `/data/{id}`                     | DELETE | Delete saved application data          |

## 🔧 Development

### Prerequisites for Development

1. **Python Environment**:

   ```bash
   # Install uv package manager (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Or use pip
   pip install uv
   ```

2. **ResumeGen Services**:

   ```bash
   # Clone ResumeGen repository
   git clone https://github.com/JakobGruen/ResumeGen.git

   # Follow ResumeGen setup instructions
   ```

3. **Node.js**: Required for ResumeGen PDF service (Node.js 16+)

### Local Development Setup

1. **Install ResumeTailor**:

   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

2. **Set up ResumeGen services**:

   ```bash
   # Clone and setup ResumeGen (required dependency)
   git clone https://github.com/JakobGruen/ResumeGen.git
   cd ResumeGen

   # Install and start PDF service
   cd PdfService
   npm install
   npm start  # Runs on port 3000

   # In another terminal, start ResumeGen API
   cd ../
   pip install -e .
   python -m resumegen.api  # Runs on port 8000
   ```

3. **Configure environment**:

   ```bash
   export OPENAI_API_KEY="your-api-key"
   export RESUMEGEN_API_URL="http://localhost:8000"
   ```

4. **Set up resume data**:

   ```bash
   # Copy example resume (contains sample data)
   cp data/full_resume.yaml.example data/full_resume.yaml
   ```

5. **Start ResumeTailor**:

   ```bash
   # API server with auto-reload
   uvicorn resumetailor.main:app --reload --port 8080
   ```

6. **Access the application**:
   - API: http://localhost:8080
   - Health check: http://localhost:8080/health
   - API documentation: http://localhost:8080/docs

### 📁 Project Structure

```
ResumeTailor-cli/
├── resumetailor/           # Main application package
│   ├── api/               # FastAPI routers and endpoints
│   ├── core/              # Core business logic and session management
│   ├── llm/               # LLM integration and prompt templates
│   ├── models/            # Pydantic data models
│   ├── services/          # Utility services and storage
│   └── main.py           # FastAPI application entry point
├── data/                  # Resume data and application history
│   ├── full_resume.yaml  # Your complete resume (YAML format)
│   ├── full_resume.json  # Your complete resume (JSON format)
│   └── private_info.json # Personal information (private)
├── tests/                 # Test suite
├── docker-compose.yml     # Multi-service Docker setup
├── Dockerfile.resumetailor # ResumeTailor container definition
└── pyproject.toml        # Python project configuration
```

### 🧪 Testing

Run the test suite with parallel execution:

```bash
# Using pytest directly
pytest -n auto

# Or using uv
uv run pytest

# Run specific test categories
pytest -m "api"          # API tests only
pytest -m "job_profile"  # Job profile tests
pytest -m "resume"       # Resume-related tests
pytest -m "cover_letter" # Cover letter tests
pytest -m "session"      # Session managements tests
pytest -m "data"         # Data management tests
pytest -m "langsmith"    # Tests that are tracked by LangSmith
pytest -m "resumegen"    # Tests that require resumegen to be running on port 8000
pytest -m "docker"       # Docker tests
```

## 📋 Dependencies

### Core Dependencies

- **FastAPI**: Web framework for API
- **LangChain**: LLM integration framework
- **LangGraph**: Multi-agent workflow orchestration
- **OpenAI**: GPT model access
- **Pydantic**: Data validation and serialization

### External Services

- **ResumeGen**: Document generation microservice
- **OpenAI GPT**: Language model for content generation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Troubleshooting

### Common Issues

1. **OpenAI API Errors**:

   - Ensure your API key is set correctly
   - Check your OpenAI account has sufficient credits
   - Verify the API key has proper permissions

2. **ResumeGen Service Connection Issues**:

   - Ensure ResumeGen services are running on ports 3000 and 8000
   - Check the `RESUMEGEN_API_URL` environment variable
   - Verify network connectivity between services

3. **Docker Build Issues**:

   - Check Docker has sufficient resources allocated
   - Verify internet connectivity for downloading dependencies
   - Ensure Docker daemon is running properly

4. **PDF Generation Failures**:
   - Ensure PDF service is running and healthy
   - Check Chrome/Chromium is properly installed in PDF service container
   - Verify sufficient memory allocation for PDF rendering

### Getting Help

- Check the [Issues](link-to-issues) page for known problems
- Review the [API documentation](http://localhost:8080/docs) when running locally
- Examine service logs: `docker-compose logs [service-name]`

---

Made with ❤️ for better job applications
