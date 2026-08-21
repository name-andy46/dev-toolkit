# <Capability> — delta for <change-id>

> One delta spec per capability this change touches. The filename (`<capability>.md`) maps to
> `docs/specs/<capability>/spec.md`. Each requirement carries exactly one **Type:** tag.
> ADDED/MODIFIED requirements need ≥1 scenario with GIVEN, WHEN, THEN. REMOVED needs none.

### Requirement: <short name>
**Type:** ADDED
<statement — SHALL / MUST phrasing encouraged>

#### Scenario: <short name>
- GIVEN <precondition>
- WHEN <action>
- THEN <expected outcome>

<!--
### Requirement: <existing requirement name, verbatim from the source spec>
**Type:** MODIFIED
<the new statement>

#### Scenario: <name>
- GIVEN ...
- WHEN ...
- THEN ...

### Requirement: <existing requirement name, verbatim from the source spec>
**Type:** REMOVED
<why it's going away — no scenario required>
-->
