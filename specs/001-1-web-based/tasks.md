# Tasks: Web-Based Network Mapping and Troubleshooting Application

**Input**: Design documents from `/specs/001-1-web-based/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Web app**: `backend/src/`, `frontend/src/`

## Phase 3.1: Setup
- [ ] T001 [P] Create backend project structure and initialize FastAPI project in `backend/`
- [ ] T002 [P] Create frontend project structure and initialize React.js project in `frontend/`
- [ ] T003 [P] Configure linting and formatting tools for both backend and frontend.
 - [ ] T003a [P] Create `backend/requirements.txt` or `pyproject.toml` and `frontend/package.json` with basic deps.
 - [ ] T003b [P] Add `docker-compose.yml` at repository root for local quickstart (referenced by `quickstart.md`).

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Contract test for POST /auth/login in `backend/tests/contract/test_auth.py`
- [ ] T005 [P] Contract test for GET /configurations in `backend/tests/contract/test_configurations.py`
- [ ] T006 [P] Integration test for user login and authentication flow in `backend/tests/integration/test_auth_flow.py`
- [ ] T007 [P] Integration test for creating and retrieving network configurations in `backend/tests/integration/test_configurations_flow.py`
 - [ ] T004a [P] Contract test for POST /what-if in `backend/tests/contract/test_what_if.py`
 - [ ] T004b [P] Contract test for POST /drift-detection in `backend/tests/contract/test_drift_detection.py`
 - [ ] T004c [P] Contract tests for /custom-compliance-policies in `backend/tests/contract/test_custom_compliance_policies.py`
 - [ ] T004d [P] Contract tests for /saved-views in `backend/tests/contract/test_saved_views.py`
 - [ ] T004e [P] Contract tests for /dashboard/widgets in `backend/tests/contract/test_dashboard_widgets.py`
 - [ ] T004f [P] Contract tests for /credential-groups in `backend/tests/contract/test_credential_groups.py`
 - [ ] T004g [P] Add test skeletons that assert endpoints return 501/NotImplemented or similar (so tests fail) in `backend/tests/contract/__init__.py`.
 - [ ] T004h [P] Add CI workflow file `backend/.github/workflows/ci.yml` (or repo-level `.github/workflows/ci.yml`) that runs contract and integration tests and enforces the TDD gate.

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T008 [P] Implement User model in `backend/src/models/user.py`
- [ ] T009 [P] Implement NetworkConfiguration model in `backend/src/models/network_configuration.py`
- [ ] T010 [P] Implement NetworkDevice model in `backend/src/models/network_device.py`
- [ ] T011 [P] Implement FirewallRule model in `backend/src/models/firewall_rule.py`
- [ ] T012 [P] Implement AuditLog model in `backend/src/models/audit_log.py`
- [ ] T013 [P] Implement ComplianceReport model in `backend/src/models/compliance_report.py`
- [ ] T014 [P] Implement DiagnosticTest model in `backend/src/models/diagnostic_test.py`
- [ ] T015 Implement authentication service in `backend/src/services/auth_service.py`
- [ ] T016 Implement configuration service in `backend/src/services/configuration_service.py`
 - [ ] T015a [P] Implement authentication service tests in `backend/tests/unit/test_auth_service.py`
 - [ ] T015b [P] Implement configuration service tests in `backend/tests/unit/test_configuration_service.py`
- [ ] T017 Implement POST /auth/login endpoint in `backend/src/api/auth.py`
- [ ] T018 Implement GET and POST /configurations endpoints in `backend/src/api/configurations.py`

## Phase 3.4: Integration
- [ ] T019 Connect services to the database.
- [ ] T020 Implement authentication middleware.
- [ ] T021 Set up request/response logging.
- [ ] T021a [P] Implement encryption for storing SSH credentials in the database.
 - [ ] T021b [P] Define credential storage strategy and KMS/local-encryption plan in `backend/docs/credentials.md`.

## Phase 3.5: Polish
- [ ] T022 [P] Write unit tests for all services.
- [ ] T023 [P] Write API documentation.

## Frontend-specific exact paths (clarifications)
To follow the spec rule of explicit file paths, frontend tasks should target concrete files. Suggested additions (map these to existing UI tasks):
- `frontend/src/pages/Settings/CredentialGroupsPage.jsx` (for T045)
- `frontend/src/components/EndpointConfig/CredentialSelect.jsx` (for T046)
- `frontend/src/components/NetworkMap/layouts/ForceDirectedLayout.jsx` (for T051)
- `frontend/src/components/NetworkMap/layouts/HierarchicalLayout.jsx` (for T051)
- `frontend/src/components/NetworkMap/Annotations/AnnotationBox.jsx` (for T052)
- `frontend/src/components/Upload/DragDropUploader.jsx` (for T053)
- `frontend/src/components/NetworkMap/ContextMenu.jsx` (for T054)
- `frontend/src/utils/shortcuts.js` (for T055)
- `frontend/src/theme/themeProvider.jsx` (for T056)
- `frontend/src/styles/responsive.css` (for T057)

Add corresponding tasks or update existing ones to reference these exact paths.

## Dependencies
- T001, T002, T003 must be completed before all other tasks.
- T004-T007 must be completed before T008-T018.
- T008-T014 can be done in parallel.
- T015 and T016 depend on the models from T008-T014.
- T017 and T018 depend on the services from T015 and T016.
- T019-T021 depend on the completion of the core implementation.
- T022-T023 can be done in parallel after the core implementation is complete.

## Parallel Example
```
# Launch T004-T007 together:
Task: "Contract test for POST /auth/login in backend/tests/contract/test_auth.py"
Task: "Contract test for GET /configurations in backend/tests/contract/test_configurations.py"
Task: "Integration test for user login and authentication flow in backend/tests/integration/test_auth_flow.py"
Task: "Integration test for creating and retrieving network configurations in backend/tests/integration/test_configurations_flow.py"
```

## Phase 3.6: Enhanced Diagnostics
- [ ] T024 [P] Implement "What-If" rule modeling service in `backend/src/services/what_if_service.py`
- [ ] T025 [P] Implement POST /what-if endpoint in `backend/src/api/what_if.py`
- [ ] T026 [P] Implement configuration drift detection service in `backend/src/services/drift_detection_service.py`
- [ ] T027 [P] Implement POST /drift-detection endpoint in `backend/src/api/drift_detection.py`
- [ ] T028 [P] Implement automated troubleshooting service in `backend/src/services/troubleshooting_service.py`

## Phase 3.7: Deeper Auditing & Compliance
- [ ] T029 [P] Implement custom compliance policy model in `backend/src/models/custom_compliance_policy.py`
- [ ] T030 [P] Implement custom compliance policy service in `backend/src/services/custom_compliance_policy_service.py`
- [ ] T031 [P] Implement GET and POST /custom-compliance-policies endpoints in `backend/src/api/custom_compliance_policies.py`
- [ ] T032 [P] Implement automated remediation suggestion service in `backend/src/services/remediation_service.py`

## Phase 3.8: Improved User Experience & Collaboration
- [ ] T033 [P] Implement saved view model in `backend/src/models/saved_view.py`
- [ ] T034 [P] Implement saved view service in `backend/src/services/saved_view_service.py`
- [ ] T035 [P] Implement GET and POST /saved-views endpoints in `backend/src/api/saved_views.py`
- [ ] T036 [P] Implement dashboard widget model in `backend/src/models/dashboard_widget.py`
- [ ] T037 [P] Implement dashboard widget service in `backend/src/services/dashboard_widget_service.py`
- [ ] T038 [P] Implement GET and POST /dashboard/widgets endpoints in `backend/src/api/dashboard_widgets.py`
- [ ] T039 [P] Implement real-time collaboration features using Socket.io.

## Phase 3.9: Non-Functional Requirements
- [ ] T040 [P] Implement detailed error handling for all API endpoints.
- [ ] T041 [P] Implement structured logging throughout the application.

## Phase 3.10: Credential Management
- [ ] T042 [P] Implement `CredentialGroup` model in `backend/src/models/credential_group.py`
- [ ] T043 [P] Implement CRUD service for `CredentialGroup` in `backend/src/services/credential_group_service.py`
- [ ] T044 [P] Implement CRUD API for `/credential-groups` in `backend/src/api/credential_groups.py`
- [ ] T045 [P] Design and implement the settings page for managing predefined credential groups in the frontend.
- [ ] T046 [P] Update the endpoint configuration page in the frontend to include the credential selection dropdown and unique credential input.
- [ ] T047 Update the SSH service to handle both individual and predefined credentials.

Replace T045/T046 with explicit paths:
- [ ] T045 [P] Design and implement the settings page for managing predefined credential groups in `frontend/src/pages/Settings/CredentialGroupsPage.jsx`.
- [ ] T046 [P] Update the endpoint configuration page in `frontend/src/components/EndpointConfig/CredentialSelect.jsx` to include the credential selection dropdown and unique credential input.

## Phase 3.11: UI/UX Enhancements
- [ ] T048 [P] Implement a welcome tour for new users.
- [ ] T049 [P] Design and implement helpful empty states for all data views.
- [ ] T050 [P] Add a feature to load sample configuration data.
- [ ] T051 [P] Implement layout options (hierarchical, force-directed) for the network map.
- [ ] T052 [P] Implement custom grouping and annotation features on the network map.
- [ ] T053 [P] Implement drag-and-drop file uploads for configuration files.
- [ ] T054 [P] Implement context menus for nodes on the network map.
- [ ] T055 [P] Implement keyboard shortcuts for common actions.
- [ ] T056 [P] Implement a light/dark mode theme for the application.
- [ ] T057 [P] Ensure the application has a responsive design that works on tablets.
