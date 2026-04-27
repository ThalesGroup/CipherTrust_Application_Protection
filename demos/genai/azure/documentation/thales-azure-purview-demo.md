# Thales + Azure Purview + Azure AI Language PII Detection

## Page 1: Discover What Matters

Modern AI and analytics projects fail when teams treat all data the same.

This solution helps organizations discover which assets actually contain sensitive data before those assets are used for retrieval, training, analytics, or sharing. Microsoft Purview scans Azure Storage, ADLS Gen2, and Azure SQL to identify the assets and columns that matter most. Instead of processing everything, the workflow focuses on the content Purview already knows is high risk.

### Business value

- Reduce unnecessary inspection of low-risk content
- Align protection workflows with enterprise governance
- Create an auditable bridge between cataloging and enforcement
- Show security teams that AI pipelines start with data discovery, not guesswork

### Core message

Purview tells you what is sensitive. Thales helps ensure that what is sensitive stays protected.

---

## Page 2: Protect Data Before It Reaches AI

Once Purview identifies the sensitive assets, the application processes them using Azure AI Language PII detection and Thales CipherTrust.

For file-based content, the app streams the exact Purview-selected blobs directly from Azure Storage, uses the Azure AI Language PII detection API to identify sensitive values in the content, and protects those values before writing the result back to a governed destination. For Azure SQL, Purview identifies the sensitive columns and the app protects only those columns before loading a protected target table.

### What this enables

- Protect data before vector-store ingestion
- Reduce raw PII exposure in prompts and retrieval results
- Preserve data utility while minimizing disclosure risk
- Support governed AI pipelines without rewriting the enterprise data estate

### Representative use cases

- RAG content preparation
- AI training-data reduction
- Sensitive-data remediation
- Governed analytics extracts
- Secure data-sharing workflows

---

## Page 3: Turn Governance Into Action

The real value of this solution is operational. It connects discovery, classification, and protection in a single story that both technical and executive audiences understand.

Security and data-governance teams can use Purview to prove where sensitive data exists. Application and platform teams can use Thales CipherTrust to protect that data before it reaches downstream AI and analytics systems. The result is a more credible enterprise AI architecture: discover first, protect second, then use data with confidence.

### Why this demo resonates

- It shows governance producing a concrete technical outcome
- It demonstrates AI readiness instead of only AI experimentation
- It helps customers connect Microsoft and Thales capabilities in one flow
- It creates a practical path from raw data to governed AI consumption

### Closing statement

Find sensitive data with Purview. Detect precise values with Azure AI Language PII detection. Protect them with Thales. Build AI on safer data.
