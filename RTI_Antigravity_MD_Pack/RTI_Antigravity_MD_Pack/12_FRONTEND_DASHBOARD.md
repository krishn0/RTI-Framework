# Citizen Transparency Dashboard Specification

## Owner
Primary: Krishna

## Objective
Integrate the intelligence layer into the existing React application without rebuilding the current search/admin interfaces.

## Required Screens

### 1. Investigation / Ask RTI AI
Elements:
- query input
- optional department/location/date filters
- start investigation button
- clear disclaimer that results are evidence-based public-record analysis

### 2. Investigation Progress
Show high-level stages only:
- understanding query
- retrieving evidence
- agent analysis
- verification
- gap detection
- report ready

Do not expose hidden chain-of-thought. Show process status, not private reasoning.

### 3. Evidence Report
Each finding must show:
- claim
- status
- source document
- page/timestamp
- source URL/open action
- evidence excerpt if appropriate

### 4. Known vs Missing
Two clearly distinct sections:
- Known / Supported
- Missing / Unresolved

### 5. Project Digital Twin
Summary cards:
- project name
- department
- location
- scheme
- sanctioned amount
- tender value
- contractor
- original deadline
- revised deadline
- evidence status

### 6. Timeline
Chronological project events with source link on selection.

### 7. Money Trail
Show separate stages:
- sanction
- estimate
- award
- release
- payment
- expenditure

Never display different financial stages as if they should match exactly.

### 8. Contradictions
For each:
- claim A
- claim B
- dates
- sources
- resolution state

### 9. RTI Draft
- editable questions
- authority
- subject
- copy/export
- link each question back to the evidence gap that generated it

### 10. RTI Response Analysis
- upload
- processing state
- table of question vs response classification
- newly resolved gaps

## UX States Required
Every screen must handle:
- loading
- empty
- partial result
- backend error
- agent error
- no evidence found
- unsupported file

## Accessibility
- keyboard navigation
- semantic labels
- no color-only status indicators
- readable contrast
