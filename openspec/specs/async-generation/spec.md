# Async Pattern Generation Specification

## ADDED Requirements

### Requirement: Headless Pattern Rendering Container
The system SHALL provide a Docker container wrapping the Seamly2D headless CLI so that
pattern files can be rendered to final output formats (PDF, DXF, SVG, PNG) without a GUI.

#### Scenario: Render a pattern to PDF
- **GIVEN** a user has selected a template and provided measurements
- **WHEN** the system invokes the render container with a `.vit` file and target format PDF
- **THEN** the container writes a `.vit` file next to the pattern, re-computes the geometry
- **AND** the system returns the rendered PDF for download

#### Scenario: Container invocation fails
- **GIVEN** the Seamly2D CLI returns a non-zero exit code (V_EX_DATAERR)
- **WHEN** the system tries to render a pattern
- **THEN** the system SHALL capture the stderr/stderr output
- **AND** return a structured error to the caller instead of a partial file

### Requirement: Async Job Queue
The system SHALL queue long-running pattern generation tasks so the API does not block.

#### Scenario: Submit generation and poll status
- **GIVEN** the API receives a generation request
- **WHEN** the hold time exceeds a short synchronous threshold
- **THEN** the API enqueues a Celery task
- **AND** returns a `job_id`
- **AND** the client polls a status endpoint until the job is `SUCCESS`, `FAILURE`, or `PENDING`
- **AND** on success the client can download the generated output

#### Scenario: Task failure and retry
- **GIVEN** a Celery worker fails while rendering a pattern
- **WHEN** the failure is transient
- **THEN** the task SHALL be retried with backoff
- **AND** the terminal failure is reported to the client via the status endpoint

### Requirement: Template Metadata Store
The system SHALL store template metadata (name, category/gender, image, required
measurements, file path) independently of the code registry so new templates can be
added without code changes.

#### Scenario: Add a new template via metadata
- **GIVEN** an operator uploads a `.val`/`.sm2d` file and its metadata
- **WHEN** the upload, validation and registration are complete
- **THEN** the template becomes available in the catalog
- **AND** users can select it and generate patterns from it
