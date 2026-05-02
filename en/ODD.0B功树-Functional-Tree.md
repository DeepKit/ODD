---
version: 1.1.0
status: stable
last_updated: 2026-02-11
prerequisites: [ODD.07产物-Artifact-Taxonomy]
---

# Functional Tree

## Intent
Artifacts grow continuously, pipelines are orchestrated continuously — but no one can answer "Where exactly is that feature I want?".
The Functional Tree is the directory of the artifact network: a layered index by business function, allowing anyone to find corresponding artifacts, contracts, and pipelines starting from a feature, and also know immediately which features are affected when an artifact changes.

## Specification

### Functional Tree Definition
Functional Tree = Layered index with business functions as nodes and "implementation/dependency" as edges.

Core Rules:
- The Functional Tree MUST cover all business functions of the project; "homeless" artifacts are not allowed.
- Each leaf node MUST map to at least one artifact.
- An artifact MAY be referenced by multiple functional nodes (Shared components).
- The granularity of Functional Tree nodes is not constrained by code modules — it is divided by business capability, not directory structure.

### Node Structure
```yaml
Functional Node:
  id: string              # Unique Identifier
  name: string            # Feature Name
  parent: string | null   # Parent Node ID, null for root
  children: [string]      # Child Node ID List
  artifacts: [string]     # Mapped Artifact ID List
  owner: string           # Owner
  status: active | deprecated | planned
```

### Key Operations
- **Locate**: Given a feature name, find corresponding artifacts and their statuses.
- **Trace**: Given an artifact, find which functional nodes it belongs to.
- **Impact Analysis**: When an artifact changes, find all affected features along the functional tree + dependency graph.
- **Coverage Check**: Detect if there are artifacts not belonging to any functional node (Orphan artifacts).

### Relationship with Pipeline/Dependency Graph
- Functional Tree manages "Business View Location", Dependency Graph manages "Technical View Propagation".
- Impact Analysis = Functional Tree Location + Dependency Graph Propagation: First calculate the set of affected artifacts on the dependency graph, then map out the set of affected features on the functional tree.
- Functional Tree does not replace Dependency Graph; they complement each other.

---

## Mechanism

### L1 · Lightweight

Functional Tree = A Markdown list, manually maintained.

**Practice**:
Place a `FunctionalTree.md` in the project root (or embedded in README), listing corresponding artifacts by business function.

```markdown
# Functional Tree

## User Management
- Registration Function → `user-register` Contract → Artifacts: user-register-api, user-register-test
- Login Function → `user-login` Contract → Artifacts: user-login-api, user-login-test

## Order Processing
- Create Order → `order-create` Contract → Artifacts: order-create-api, order-create-test
- Payment → `order-pay` Contract → Artifacts: order-pay-api, payment-gateway-adapter
```

**Impact Analysis**: Manual. When an artifact changes, search for the artifact in the list to see which features it belongs to.

**Coverage Check**: Manual comparison of artifact list and functional tree to confirm no omissions.

---

### L2 · Standard

Functional Tree = Structured Data, Tool Queryable.

**Node Definition**:
```yaml
functional_tree:
  nodes:
    - id: user-mgmt
      name: User Management
      parent: null
      children: [user-register, user-login]
      artifacts: []
      owner: team-a
      status: active

    - id: user-register
      name: Registration Function
      parent: user-mgmt
      children: []
      artifacts: [user-register-api, user-register-test]
      owner: team-a
      status: active
```

**Query Capabilities**:
- `locate(feature_name)` → Returns artifact ID list and their current status (sealed / stale / in_progress).
- `trace(artifact_id)` → Returns the list of functional nodes the artifact belongs to.
- `orphans()` → Returns the list of artifacts not belonging to any functional node.

**Impact Analysis**:
```
Artifact X changes
  → Dependency Graph: Find downstream affected artifact set S
  → Functional Tree: Call trace() for each artifact in S, get affected feature set F
  → Output: Feature list F + affected artifacts under each feature
```

**Data Structure**:
```yaml
functional_node:
  id: string
  name: string
  parent: string | null
  children: [string]
  artifacts: [artifact_id]
  owner: string
  status: active | deprecated | planned
  updated_at: datetime
```

---

### L3 · Strict

Functional Tree = Auditable Business Index, Forced Coverage, Auto Synchronization, Change Tracking.

**Mandatory Rules**:
- Each artifact MUST belong to at least one functional node, otherwise sealing gate rejects.
- Functional node changes (Add/Remove/Remap) MUST be recorded in audit logs.
- Functional Tree version MUST align with artifact seal version — Functional Tree snapshot at sealing time acts as part of evidence.

**Auto Synchronization**:
- When new artifact is created, system prompts to attribute to a functional node (or reject creation).
- When artifact is deleted/deprecated, automatically remove mapping from functional tree, mark orphan nodes.

**Impact Analysis Enhancement**:
```
Artifact X changes
  → Dependency Graph: Cascading calculation of affected artifact set S
  → Functional Tree: Map out affected feature set F
  → Auto notify owner of each feature in F
  → Audit Log Record: Change Source → Impact Scope → Notification Target → Handling Result
```

**Data Structure Increment**:
```yaml
functional_node:
  # ...L2 fields...
  version: integer                    # Node Version
  change_log:
    - changed_at: datetime
      change_type: add_artifact | remove_artifact | remap | deprecate
      detail: string
      operator: string

functional_tree_snapshot:
  snapshot_id: string
  tree_version: integer
  taken_at: datetime
  triggered_by: string                # Which seal triggered the snapshot
  nodes: [functional_node]
```

---

### Complete Example: E-commerce System Functional Tree

The following shows a typical e-commerce system functional tree structure, artifact mapping, and impact analysis.

#### Functional Tree Structure

```
E-commerce Platform (root)
├── User Management (user-mgmt)
│   ├── Registration (user-register)
│   ├── Login (user-login)
│   └── Profile (user-profile)
├── Product Management (product-mgmt)
│   ├── Product List (product-list)
│   ├── Product Search (product-search)
│   └── Inventory (inventory)
├── Order Management (order-mgmt)
│   ├── Create Order (order-create)
│   ├── Payment (order-pay)
│   └── Refund (order-refund)
└── Notification System (notification)
    ├── Email Notification (notify-email)
    └── Inbox Message (notify-inbox)
```

#### L2 Structured Data (Excerpt)

```yaml
functional_tree:
  nodes:
    - id: root
      name: E-commerce Platform
      parent: null
      children: [user-mgmt, product-mgmt, order-mgmt, notification]
      artifacts: []
      owner: platform-team
      status: active

    - id: order-mgmt
      name: Order Management
      parent: root
      children: [order-create, order-pay, order-refund]
      artifacts: []
      owner: order-team
      status: active

    - id: order-create
      name: Create Order
      parent: order-mgmt
      children: []
      artifacts:
        - order-create-api          # REST API Artifact
        - order-create-validator    # Input Validator Artifact
        - order-create-test         # Test Artifact
      owner: order-team
      status: active

    - id: order-pay
      name: Payment
      parent: order-mgmt
      children: []
      artifacts:
        - payment-gateway-adapter   # Payment Gateway Adapter
        - payment-callback-handler  # Callback Handler
        - payment-test              # Payment Test
      owner: order-team
      status: active

    - id: order-refund
      name: Refund
      parent: order-mgmt
      children: []
      artifacts:
        - refund-processor          # Refund Processor
        - refund-policy-engine      # Refund Policy Engine
      owner: order-team
      status: active

    - id: inventory
      name: Inventory Management
      parent: product-mgmt
      children: []
      artifacts:
        - inventory-service         # Inventory Service
        - inventory-lock            # Inventory Locking Mechanism
      owner: product-team
      status: active
```

#### Impact Analysis Demo

**Scenario**: `payment-gateway-adapter` artifact changes (Payment gateway upgrade).

```
Step 1: Dependency Graph Propagation
  payment-gateway-adapter Change
    → payment-callback-handler (Direct Dependency)
    → refund-processor (Calls payment interface for refund)
    → order-create-api (Calls payment interface for deduction)
  Affected Artifact Set S = {
    payment-callback-handler,
    refund-processor,
    order-create-api
  }

Step 2: Functional Tree Mapping
  trace(payment-callback-handler) → Payment (order-pay)
  trace(refund-processor)          → Refund (order-refund)
  trace(order-create-api)          → Create Order (order-create)
  Affected Feature Set F = {Payment, Refund, Create Order}

Step 3: Output
  Affected Feature | Affected Artifact         | Owner
  ─────────────────┼───────────────────────────┼──────────
  Payment          | payment-callback-handler  | order-team
  Refund           | refund-processor          | order-team
  Create Order     | order-create-api          | order-team

  → Notify order-team: 3 features affected, need to re-verify downstream artifacts.
```

#### Coverage Check Example

```
orphans() → Returns: [logging-middleware]

→ Found orphan artifact: logging-middleware does not belong to any functional node.
→ Action: Attribute to "Infrastructure" functional node, or mark deprecated if confirmed obsolete.
```

---

## Practice

### Quick Selection Guide
- **Artifacts < 20** → L1, A Markdown list is sufficient.
- **Multi-team collaboration, continuous artifact growth** → L2, Structured data + Query capability.
- **Need compliance audit, no orphan artifacts allowed** → L3, Forced coverage + Version snapshot + Change audit.

### Core Principles
- **Function View First**: Functional Tree organized by "What users want", not "How code is divided".
- **Zero Orphans**: Every artifact can find its home in the Functional Tree, no "ghost artifacts".
- **Dual View Complement**: Functional Tree = Business Map, Dependency Graph = Technical Path. Combining both answers "If I change this, which businesses are affected".
