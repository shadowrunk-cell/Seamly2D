# Monetization Specification

## ADDED Requirements

### Requirement: Freemium License Model
The system SHALL offer both free and premium tiers.

#### Scenario: Free tier usage
- **GIVEN** a user downloads SeamlyAI
- **WHEN** the user uses the application without a license
- **THEN** the user has access to:
  - Full pattern construction and editing
  - Limited AI generations (5 per day)
  - Local AI processing (slower, less accurate)
  - Export to DXF (basic), SVG, PDF

#### Scenario: Premium tier features
- **GIVEN** a user purchases a premium license
- **WHEN** the user logs in with their premium account
- **THEN** the user has access to:
  - Unlimited AI generations
  - Cloud AI processing (faster, more accurate)
  - Premium export formats (DXF-ASTM with full curve data)
  - Cloud storage and syncing
  - Team collaboration features
  - Priority support

### Requirement: Cloud Storage for Premium Users
The system SHALL provide cloud storage for patterns and preferences.

#### Scenario: Save pattern to cloud
- **GIVEN** a premium user is working on a pattern
- **WHEN** the user saves the pattern
- **THEN** the pattern is synced to the user's cloud storage
- **AND** is accessible from other devices

#### Scenario: Collaborate on a pattern
- **GIVEN** two premium users are working on the same team
- **WHEN** one user modifies a shared pattern
- **THEN** the other user sees the changes in real-time (or upon refresh)
- **AND** version history is maintained
