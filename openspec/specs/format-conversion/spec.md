# Format Conversion Specification

## ADDED Requirements

### Requirement: DXF-ASTM Export for CLO 3D
The system SHALL export patterns in DXF-ASTM format with preserved curve information.

#### Scenario: Export to CLO 3D
- **GIVEN** a user has a completed 2D pattern
- **WHEN** the user selects "Export to CLO 3D (DXF-ASTM)"
- **THEN** the system generates a DXF file with:
  - All splines correctly marked as splines (not polyline approximations)
  - Notches and grain lines preserved as metadata
  - Pattern pieces named and grouped
  - ASTM format compliant

#### Scenario: Export fails validation
- **GIVEN** a user attempts to export a pattern with self-intersecting curves
- **WHEN** the export is initiated
- **THEN** the system SHALL validate the pattern geometry
- **AND** display a warning with specific error locations
- **AND** allow the user to fix issues before retrying

### Requirement: OBJ/FBX Export for Blender
The system SHALL export patterns as 3D meshes for use in Blender.

#### Scenario: Export flat pattern as OBJ
- **GIVEN** a user has a 2D pattern
- **WHEN** the user selects "Export to OBJ"
- **THEN** the system generates a flat 3D mesh of the pattern
- **AND** includes material information for fabric simulation

### Requirement: Import from Existing CAD Formats
The system SHALL import patterns from common CAD formats (DXF, AAMA, ASTM).

#### Scenario: Import DXF from competitor CAD
- **GIVEN** a user has a DXF file from Gerber or Lectra
- **WHEN** the user selects "Import DXF"
- **THEN** the system imports the pattern with:
  - All geometry intact
  - Measurements preserved
  - Grading information (if present) imported

### Requirement: SM2D Native Pattern Format
The system SHALL write and read patterns in the modern `.sm2d` format in addition to the
legacy `.val` format.

#### Scenario: Save a pattern as .sm2d
- **GIVEN** a user has a completed pattern
- **WHEN** the user saves the pattern
- **THEN** the system writes a `.sm2d` file
- **AND** the file opens correctly in Seamly2D (>= 2023)

#### Scenario: Convert legacy .val to .sm2d
- **GIVEN** a user has a legacy `.val` template
- **WHEN** the user converts it to the canonical format
- **THEN** the system converts the file via the Seamly2D converter
- **AND** preserves all measurements references, increments, and geometry

### Requirement: Measurement File Interchange (.vit)
The system SHALL generate and apply a `.vit` measurement file for a selected pattern, so
changing measurement values rebuilds the pattern geometry.

#### Scenario: Apply measurements to a template
- **GIVEN** a user provides measurements for a chosen template
- **WHEN** the system generates the pattern
- **THEN** the system produces a `.vit` file with the user's values
- **AND** substitutes the `.vit` path into the `.val`/`.sm2d` template
- **AND** the geometry re-computes accordingly in Seamly2D

