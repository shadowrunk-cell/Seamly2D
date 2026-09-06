# Pattern Generation Specification

## ADDED Requirements

### Requirement: AI-Pattern Generation from Sketch
The system SHALL generate parametric patterns from user-uploaded sketches or photographs.

#### Scenario: Generate basic bodice from photo
- **GIVEN** a user uploads a photo of a dress sketch
- **AND** the user provides body measurements (height, bust, waist, hip)
- **WHEN** the user invokes the AI pattern generator
- **THEN** the system returns a parametric pattern with all measurements applied
- **AND** the pattern is editable in the 2D workspace

#### Scenario: Pattern generation fails
- **GIVEN** a user uploads a low-quality or unrecognizable sketch
- **WHEN** the AI pattern generator fails to generate a valid pattern
- **THEN** the system SHALL display a clear error message
- **AND** suggest alternative approaches (e.g., use template, manual drawing)

### Requirement: AI-Assisted Gradation
The system SHALL automatically grade patterns across multiple sizes using AI.

#### Scenario: Grade pattern to size range
- **GIVEN** a user has a finished pattern in size M
- **WHEN** the user selects "Generate Size Range" with sizes XS to XL
- **THEN** the system generates all intermediate sizes
- **AND** each size follows standard industry grading rules
- **AND** the user can review and adjust each grade individually

### Requirement: Natural Language Parameter Adjustment
The system SHALL allow users to modify pattern parameters using natural language.

#### Scenario: Adjust sleeve length by voice
- **GIVEN** a user has an open pattern with a sleeve
- **WHEN** the user types or speaks "make sleeves 5 cm shorter"
- **THEN** the system automatically updates the sleeve pattern
- **AND** all dependent measurements (armhole, cuff) are updated accordingly
