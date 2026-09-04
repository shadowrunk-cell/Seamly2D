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
