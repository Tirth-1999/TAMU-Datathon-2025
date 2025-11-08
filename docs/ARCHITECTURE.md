# System Architecture

## AI-Powered Regulatory Document Classifier

### Overview
The Regulatory Document Classifier is a full-stack AI application designed to automatically classify documents into sensitivity categories while maintaining audit trails and supporting human-in-the-loop workflows.

---

## System Components

### 1. Backend Services (Python/FastAPI)

#### Core Services

**Document Processor** (`backend/services/document_processor.py`)
- Multi-modal document parsing (PDF, images)
- OCR integration for image-based documents
- Pre-processing checks (legibility, page count, image count)
- Text extraction and content aggregation

**PII Detector** (`backend/services/pii_detector.py`)
- Pattern-based PII detection (SSN, credit cards, account numbers, etc.)
- Context-aware validation
- Confidence scoring
- Redaction suggestions

**Content Safety Checker** (`backend/services/content_safety.py`)
- Multi-category safety monitoring
  - Child safety violations
  - Hate speech
  - Violence and graphic content
  - Criminal activity
  - Cyber threats
- Severity assessment
- Contextual analysis

**Classification Engine** (`backend/services/classifier.py`)
- LLM-based document classification
- Support for multiple models:
  - Primary: Claude 3 Haiku (fast, cost-effective)
  - Secondary: GPT-3.5 Turbo (verification)
- Dual-LLM cross-verification
- Citation generation
- Confidence scoring

**Prompt Manager** (`backend/services/prompt_manager.py`)
- Dynamic prompt generation
- Configurable prompt library (YAML)
- Prompt tree construction
- HITL trigger evaluation

#### API Layer

**FastAPI Application** (`backend/main.py`)
- RESTful API endpoints
- File upload handling
- Background task processing
- Real-time classification
- Feedback submission
- Document management

#### Database Layer

**Models** (`backend/models/`)
- Documents: File metadata and processing status
- Classifications: Results and confidence scores
- Citations: Evidence with page/region references
- Feedback: HITL corrections and improvements
- Audit Logs: Complete action history

---

## Classification Categories

1. **Public**
   - Marketing materials
   - Public website content
   - Press releases
   - Generic product information

2. **Confidential**
   - Internal business documents
   - Customer lists (non-PII)
   - Operational procedures
   - Strategic plans

3. **Highly Sensitive**
   - Personal Identifiable Information (PII)
   - Financial account information
   - Proprietary schematics
   - Defense/military content

4. **Unsafe**
   - Child safety violations
   - Hate speech
   - Violent content
   - Criminal instructions
   - Cyber threats

---

## Processing Pipeline

### Document Classification Flow

```
1. Upload Document
   ↓
2. Pre-processing Checks
   - Validate file type and size
   - Extract text and images
   - Calculate legibility score
   ↓
3. PII Detection
   - Scan for sensitive patterns
   - Validate with context
   - Generate PII report
   ↓
4. Content Safety Check
   - Check safety categories
   - Flag violations
   - Block if critical
   ↓
5. Primary Classification (Claude Haiku)
   - Generate dynamic prompt
   - Call LLM for classification
   - Extract reasoning and citations
   ↓
6. Dual Verification (Optional - GPT-3.5)
   - Independent classification
   - Calculate agreement score
   - Resolve conflicts
   ↓
7. Citation Generation
   - Page-level evidence
   - PII references
   - Safety violations
   - LLM-provided citations
   ↓
8. HITL Decision
   - Check confidence threshold
   - Evaluate triggers
   - Queue for review if needed
   ↓
9. Store Results
   - Save to database
   - Generate audit log
   - Return to user
```

---

## Dynamic Prompt System

The system uses a configurable YAML-based prompt library that enables:

1. **Prompt Tree Generation**
   - Stage-based prompts (initial analysis, PII detection, final classification)
   - Category-specific instructions
   - Evidence requirements

2. **Context Injection**
   - PII detection results
   - Safety check results
   - Document metadata

3. **Citation Requirements**
   - Page/image references
   - Evidence extraction
   - Relevance scoring

4. **HITL Triggers**
   - Low confidence (< 0.70)
   - Multiple categories detected
   - Conflicting signals
   - Safety flags

---

## Human-in-the-Loop (HITL) Workflow

### Trigger Conditions
1. Confidence score below threshold (0.70)
2. PII detected in potentially public document
3. Multiple categories with similar confidence
4. Safety violations requiring review
5. Dual-LLM disagreement

### Feedback Loop
1. **Review Queue**: Documents flagged for review
2. **Expert Review**: SME validates classification
3. **Feedback Capture**: Corrections and context
4. **Prompt Improvement**: Update prompt library
5. **Model Refinement**: Track improvements over time

---

## Dual-LLM Verification

### Purpose
Reduce HITL requirements by cross-verifying classifications

### Process
1. Primary model (Claude Haiku) classifies document
2. Secondary model (GPT-3.5) independently classifies
3. Compare results:
   - Category agreement
   - Confidence similarity
   - Reasoning alignment
4. Calculate agreement score
5. If agreement > 0.90: Accept classification
6. If disagreement: Trigger HITL review

### Benefits
- Increased accuracy
- Reduced human review burden
- Confidence in edge cases
- Cost-effective verification

---

## Citation and Evidence System

### Citation Types

1. **Text Citations**
   - Page number
   - Text excerpt
   - Relevance explanation

2. **PII Citations**
   - Page number
   - PII type
   - Redacted context
   - Confidence score

3. **Safety Citations**
   - Page number
   - Safety category
   - Violation description
   - Severity level

4. **Image Citations**
   - Image number
   - Region (bounding box)
   - Description
   - Relevance to classification

### Citation Storage
All citations stored in database with:
- Full traceability
- Audit compliance
- Easy retrieval
- Export capabilities

---

## Performance Optimization

### Model Selection
- **Claude 3 Haiku**: Primary model
  - Fast inference (< 2 seconds)
  - Cost-effective ($0.25/MTok input, $1.25/MTok output)
  - High accuracy for classification tasks
  - Good reasoning capabilities

- **GPT-3.5 Turbo**: Verification model
  - Fast and affordable
  - Good agreement with Claude
  - Reduces API lock-in

### Caching Strategy
- Prompt templates cached in memory
- Document content cached during processing
- Database query optimization
- Background task processing

### Batch Processing
- Queue-based document processing
- Parallel classification for multiple documents
- Real-time status updates
- Progress tracking

---

## Security and Compliance

### Data Privacy
- Uploaded documents stored securely
- PII redacted in logs and displays
- Configurable retention policies
- Secure file deletion

### Audit Trail
- Complete action history
- User tracking
- Timestamp recording
- Success/failure logging

### Access Control
- Role-based permissions (future)
- Reviewer authentication
- API key management
- Rate limiting

---

## Scalability Considerations

### Current Architecture
- SQLite for development
- Local file storage
- Synchronous processing

### Production Recommendations
1. **Database**: PostgreSQL with connection pooling
2. **File Storage**: S3 or similar cloud storage
3. **Task Queue**: Celery with Redis
4. **Caching**: Redis for frequently accessed data
5. **Load Balancing**: Multiple API instances
6. **Monitoring**: Logging aggregation and metrics

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **LLM Integration**: Anthropic Claude, OpenAI GPT
- **Document Processing**: PyPDF2, pdf2image, pytesseract
- **Database**: SQLAlchemy ORM
- **Background Tasks**: FastAPI BackgroundTasks (Celery for production)

### Models Used
- **Primary Classification**: Claude 3 Haiku (claude-3-haiku-20240307)
- **Secondary Verification**: GPT-3.5 Turbo
- **Benefits**: Cost-effective, fast, high accuracy

---

## API Endpoints

### Document Management
- `POST /api/documents/upload` - Upload document
- `POST /api/documents/{id}/classify` - Classify document
- `GET /api/documents/{id}` - Get document details
- `GET /api/documents` - List documents

### Feedback
- `POST /api/feedback` - Submit HITL feedback

### Health
- `GET /health` - Health check
- `GET /` - API info

---

## Future Enhancements

1. **Frontend UI**: React/Next.js interface
2. **Batch Processing**: Upload multiple documents
3. **Real-time Updates**: WebSocket for live status
4. **Advanced Visualizations**: Classification reports, trends
5. **Export Functions**: PDF reports, CSV data
6. **Prompt Learning**: Automated prompt optimization
7. **Video Support**: Multi-modal video analysis
8. **Advanced OCR**: Handwriting recognition
9. **Multi-language**: Support for non-English documents
10. **Integration APIs**: Connect to document management systems
