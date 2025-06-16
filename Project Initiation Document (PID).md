**Project Initiation Document (PID)**

**Project Title:** RAG‑Powered Conversational AI Web Service


---

## 1. Project Purpose

To design, develop, and deploy a secure, scalable Retrieval‑Augmented Generation (RAG) conversational AI web service that integrates TensorFlow‑Hub embeddings, Chroma vector store, and Google Generative AI to deliver context‑aware responses based on an organization’s document corpus. The service aims to streamline documentation reading by providing users with precise, context‑grounded information on demand via a RESTful Flask API.

## 2. Goals and Objectives

* **G1:** Implement a Flask‑based backend exposing chat and health endpoints.
* **G2:** Integrate TensorFlow‑Hub Universal Sentence Encoder for embedding user queries and document passages.
* **G3:** Deploy Chroma as a vector store to index and retrieve relevant documents.
* **G4:** Leverage Google Generative AI (Gemini‑1.5) to generate coherent, context‑grounded responses.

## 3. Success Criteria

1. **Functional Validation:** All REST endpoints pass integration tests for expected behavior.
2. **Operational Readiness:** Documented deployment playbooks and automated error alerts.

## 4. Assumptions and Constraints

| Assumptions                                      | Constraints                                            |
| ------------------------------------------------ | ------------------------------------------------------ |
| Access to a stable Google Generative AI key.     | Only CPU inference for TensorFlow (no GPU).            |
| Document corpus is pre‑formatted and accessible. | Budget capped at \$5,000 for initial cloud services.   |
| Flask and Python 3.9+ environment available.     | Must use Chroma vector store.                          |
| Developers have familiarity with GitHub Actions. | API key management through environment variables only. |

## 5. Business Case (Justification)

Organizations struggle to provide on‑demand, context‑aware answers by traditional chatbots due to static knowledge bases. A RAG‑powered service enhances responses by dynamically retrieving relevant document snippets and combining them with a generative model. This reduces research time, improves decision‑making, and elevates customer support quality. The ROI is realized through lowered support costs and faster information access.

## 6. Project Scope

**In Scope:**

* Flask application with `/api/chat` and `/api/health` endpoints.
* Integration of TensorFlow‑Hub embeddings and Chroma retrieval.
* Google Generative AI configuration and prompt engineering.
* Dockerization and deployment scripts.
* CI/CD workflows for automated testing and deployment.
* Basic logging and error handling.

**Out of Scope:**

* UI/UX frontend beyond API demonstration.
* Multi‑language support at launch.
* Advanced analytics dashboards.

---

## A) Problem Statement

Organizations maintain extensive document repositories but lack efficient tools to surface precise, contextually relevant information on demand. Traditional search yields keyword matches without nuanced comprehension, while static chatbots cannot incorporate up‑to‑date content. This gap leads to longer response times, reduced productivity, and sub‑optimal decision‑making.

**This project** addresses these challenges by building a RAG‑powered chat service that dynamically retrieves relevant document snippets and synthesizes them into coherent answers, ensuring users receive accurate, context‑grounded information rapidly.

## B) Requirements Document

### B.1 Functional Requirements

1. **User Query Handling:**

   * Accept POST requests to `/api/chat` with JSON payload containing `query`.
   * Validate non‑empty `query`; return HTTP 400 if missing.
2. **Document Retrieval:**

   * Load or initialize Chroma vector store from `./chroma_db`.
   * Embed incoming `query` using TensorFlow‑Hub Universal Sentence Encoder.
   * Retrieve top‑5 most relevant documents.
3. **Response Generation:**

   * Construct prompt including retrieved context snippets.
   * Call Google Generative AI (Gemini‑1.5‑flash) with configured temperature, top‑p, top‑k.
   * Return generated `answer` and list of `sources` referencing retrieved docs.
4. **Health Check:**

   * GET `/api/health` returns JSON `{"status": "healthy"}` with HTTP 200.
5. **Error Handling & Logging:**

   * Log exceptions from embedding, retrieval, and generation modules.
   * Return user‑friendly messages for service errors (HTTP 500).
6. **CI/CD Integration:**

   * GitHub Actions workflows under `.github/workflows` to run pytest integration tests.
   * Automate Docker build and push to registry.

### B.2 User Interactions / API Flows

1. **Chat Flow:**

   * **User:** Sends POST to `/api/chat` with `{"query": "..."}`.
   * **System:** Validates input; retrieves context docs; generates answer; responds with JSON:

     ```json
     {
       "answer": "...",
       "sources": ["Doc 1: fileA.txt", "Doc 2: fileB.pdf"]
     }
     ```
2. **Health Flow:**

   * **User:** Sends GET to `/api/health`.
   * **System:** Returns `{ "status": "healthy" }`.

---

*End of Project Initiation Document.*
