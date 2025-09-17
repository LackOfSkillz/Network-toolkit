# Data Model for Network Change Tracking and Auditing Platform

This document defines the data models for the key entities in the application.

## User

- **Description**: Represents a user of the application.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `username`: String, unique
  - `email`: String, unique
  - `password_hash`: String
  - `role`: String (e.g., "admin", "user")
  - `created_at`: Timestamp
  - `updated_at`: Timestamp
- **Relationships**: None

## NetworkConfiguration

- **Description**: Represents a snapshot of a network's configuration.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `name`: String
  - `description`: Text
  - `version`: Integer
  - `created_at`: Timestamp
- **Relationships**:
  - Has many `NetworkDevice`s
  - Has many `FirewallRule`s

## NetworkDevice

- **Description**: Represents a device on the network.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `name`: String
  - `type`: String (e.g., "firewall", "router", "switch")
  - `ip_address`: String
  - `mac_address`: String
  - `config`: JSONB
  - `created_at`: Timestamp
  - `updated_at`: Timestamp
- **Relationships**:
  - Belongs to a `NetworkConfiguration`

## FirewallRule

- **Description**: Represents a single rule from a firewall configuration.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `source_ip`: String
  - `destination_ip`: String
  - `port`: Integer
  - `protocol`: String
  - `action`: String (e.g., "allow", "deny")
  - `created_at`: Timestamp
  - `updated_at`: Timestamp
- **Relationships**:
  - Belongs to a `NetworkConfiguration`

## AuditLog

- **Description**: Represents a record of a change made to the network configuration.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `user_id`: Foreign key to `User`
  - `action`: String (e.g., "create", "update", "delete")
  - `entity`: String (e.g., "NetworkDevice", "FirewallRule")
  - `entity_id`: UUID
  - `changes`: JSONB
  - `created_at`: Timestamp
- **Relationships**:
  - Belongs to a `User`

## ComplianceReport

- **Description**: Represents a generated report on NERC CIP compliance.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `configuration_id`: Foreign key to `NetworkConfiguration`
  - `status`: String (e.g., "compliant", "non-compliant")
  - `details`: JSONB
  - `created_at`: Timestamp
- **Relationships**:
  - Belongs to a `NetworkConfiguration`

## DiagnosticTest

- **Description**: Represents the results of a connectivity test.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `source_ip`: String
  - `destination_ip`: String
  - `port`: Integer
  - `results`: JSONB
  - `created_at`: Timestamp
- **Relationships**: None

## CustomCompliancePolicy

- **Description**: Represents a user-defined compliance policy.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `name`: String
  - `description`: Text
  - `rules`: JSONB
  - `created_at`: Timestamp
  - `updated_at`: Timestamp
- **Relationships**: None

## SavedView

- **Description**: Represents a saved view of the network map.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `user_id`: Foreign key to `User`
  - `name`: String
  - `description`: Text
  - `view_state`: JSONB (stores zoom level, filters, etc.)
  - `created_at`: Timestamp
  - `updated_at`: Timestamp
- **Relationships**:
  - Belongs to a `User`

## DashboardWidget

- **Description**: Represents a widget on the user's dashboard.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `user_id`: Foreign key to `User`
  - `type`: String (e.g., "RecentChanges", "BlockedPorts")
  - `config`: JSONB
  - `created_at`: Timestamp
  - `updated_at`: Timestamp
- **Relationships**:
  - Belongs to a `User`

## CredentialGroup

- **Description**: Represents a predefined group of SSH credentials.
- **Fields**:
  - `id`: Unique identifier (UUID)
  - `name`: String (e.g., "Firewall Credentials")
  - `username`: String
  - `password_encrypted`: String
  - `private_key_encrypted`: String
  - `created_at`: Timestamp
  - `updated_at`: Timestamp
- **Relationships**: None
