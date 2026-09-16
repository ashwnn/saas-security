# Lab 1: Build a Small SaaS Compliance Program

## Objective

Act as InvoiceFlow's first security engineer. Build the smallest credible control system that could support a SOC 2 Security examination and an ISO/IEC 27001:2022 certification project.

This is a design and evidence lab. No compliance platform is required.

## What you should learn

- Why compliance starts with scope and risk, not a list of policies.
- How SOC 2 and ISO/IEC 27001 differ in purpose and assurance model.
- How one technical or administrative control can support multiple frameworks.
- What evidence proves a control operated, as opposed to merely existing on paper.
- Why owners, frequency, exceptions, and review records matter.

## Scenario facts

InvoiceFlow has these systems and practices:

- Production: Kubernetes cluster, managed PostgreSQL, object storage, cloud KMS, monitoring, and backups.
- Delivery: GitHub, pull requests, GitHub Actions, container registry, infrastructure as code.
- Identity: Entra ID with MFA for administrators, but not consistently for all staff.
- People: 35 employees and three contractors. One departed contractor still appears in a GitHub team.
- Vendors: cloud provider, GitHub, customer-support platform, payment provider, and email provider.
- Change management: engineers normally use pull requests, but branch protection is not enabled on every repository.
- Vulnerability management: container scans run occasionally. No formal remediation SLA exists.
- Incidents: an informal Slack channel is used. There is no approved incident-response plan or completed exercise.
- Backups: daily database backups exist. The last restore test was eight months ago and was not documented.
- Customer promise: 99.9% monthly uptime. The status page shows two outages last quarter.
- Goal: become ready for a SOC 2 Type 2 examination and ISO/IEC 27001 certification without pretending every control is already mature.

## Part 1: Define scope

Write a one-paragraph scope statement covering:

1. the product or service in scope;
2. production infrastructure and supporting systems;
3. people and locations that operate it;
4. data types and trust boundaries;
5. exclusions and why they do not threaten the scope.

> InvoiceFlow is a B2B SaaS application for creating and managing customer invoices, together with the production environment that delivers and supports the service: the Python application running on Azure Kubernetes Service (AKS), Azure Blob Storage, Azure Database for PostgreSQL, production backups, and the supporting systems and third-party services used to develop, operate, monitor, support, and secure the service, including cloud hosting, source control, customer support, payment, and email providers. The scope covers all personnel who administer, develop, support, or access production systems, including staff working from the Burnaby office and remote locations. It includes customer and user data processed by the service, such as names and email addresses, invoice contents, related notes, account data, and any financial information contained in invoices, as it crosses trust boundaries among users, InvoiceFlow’s application and personnel, Azure services, and relevant subprocessors. Non-production environments, personal devices not approved for company access, and systems unrelated to delivering or supporting InvoiceFlow are excluded because they do not store, process, or provide administrative access to production customer data or the production service.


Then answer:

- For SOC 2, which Trust Services Categories would you include initially? Security & Availability will be the two trust categories we include later on following with confidentiality. We include security as a default as it is one of the most funamental controls, for availability we require this as we boast a 99.9% uptime commitment.
- For ISO/IEC 27001, what is the ISMS boundary? For the case of Invoice Flow we could define the scope as: employees, contractors supporting (customer), development and devops personell who work on the application itself, production technology stack, the physical office itself and remote setups, customer data handled by InvoiceFlow.
- Which subservice organizations or vendors are relied upon? Azure (Cloud Provider), GitHub, Zendesk (Customer Support), Stripe (Payment Provider), M365 (Email Provider)
- Which customer responsibilities are complementary user-entity controls rather than InvoiceFlow controls? The client is in charge of: user management (on InvoiceFlow), RBAC, Credential Control, Accurate Information (for invoices), Reporting Issues and/or compromises, Securing Integrations. 

Recommended starting position: use the SOC 2 Security category first. Add Availability only if the company is prepared to support the 99.9% commitment with monitoring, incident records, capacity management, backup/restore evidence, and availability calculations. Security is the required common category in a SOC 2 examination; the other categories are selected based on commitments and risk.

## Part 2: Build the risk register

Copy `templates/risk-register.csv` and add at least eight risks. Include these six:

1. unauthorized production access;
2. vulnerable dependency reaches production;
3. unreviewed code or infrastructure change;
4. customer data disclosed through a support or logging workflow;
5. backup exists but cannot be restored within business requirements;
6. critical vendor failure or compromise.

Use a simple scoring method:

- Likelihood: 1-5
- Impact: 1-5
- Inherent risk: likelihood x impact before additional treatment
- Residual risk: estimated likelihood x impact after the control operates

For every risk, record an owner and treatment decision: mitigate, accept, transfer, or avoid. An accepted risk still needs approval, rationale, expiry/review date, and monitoring.

## Part 3: Design controls once, map them twice

Copy `templates/control-matrix.csv`. Define eight to twelve controls. Each control needs:

- a plain-language objective;
- an owner;
- a trigger or frequency;
- a precise procedure;
- retained evidence;
- an exception path;
- a test method;
- mappings to relevant SOC 2 and ISO/IEC 27001 areas.

Use these starter controls:

| Control | Implementation idea | Strong evidence |
| --- | --- | --- |
| Workforce access | Entra ID, MFA, role-based groups, joiner/mover/leaver workflow | Identity configuration, access request, termination ticket, quarterly review with reviewer sign-off |
| Production access | Separate privileged role, time-bound elevation, logged admin actions | Role assignments, elevation record, production audit logs, sampled approval |
| Change control | Protected main branch, peer review, required CI checks, deployment record | Repository settings, sampled PRs, test results, deployment record, emergency-change review |
| Vulnerability management | Scheduled scanning, severity-based SLA, ownership, exception process | Scan output, ticket history, SLA report, approved time-bound exception |
| Incident response | Approved plan, severity model, contact tree, exercise and lessons learned | Approved version, exercise record, incident ticket, corrective actions |
| Backup and recovery | Automated backups plus scheduled restore tests | Backup configuration, restore-test output, achieved RTO/RPO, failed-test remediation |
| Vendor risk | Risk-tier vendors before onboarding and annually thereafter | Inventory, completed review, contract/security terms, tracked findings |
| Logging and monitoring | Centralized production and identity logs, alert triage, retention | Configuration, alert sample, ticket, retention setting, review record |

Suggested mappings, without reproducing either framework:

- SOC 2: CC6 logical/physical access, CC7 system operations and incident response, CC8 change management, CC9 risk mitigation and vendors, plus relevant governance/risk criteria in CC1-CC5.
- ISO/IEC 27001: clauses 4-10 for the ISMS and risk process; relevant Annex A controls for access, identity, authentication, cloud services, suppliers, incidents, logging, monitoring, vulnerability management, secure development, configuration, and change management.

The mapping is not the control. The actual control is what people and systems do.

## Part 4: Perform an evidence test

Test three controls against the following samples.

### Sample A: terminated contractor

- HR termination date: June 3
- Entra account disabled: June 3
- GitHub organization membership removed: June 18
- Production group membership: never assigned
- Ticket: says "access removed" but only includes an Entra screenshot

Decide:

- Did the control operate as described?
- Is this a design gap, operating exception, or documentation gap?
- What is the risk?
- What corrective action and owner would you assign?

### Sample B: emergency deployment

- Direct push to `main` during a customer outage
- CI tests passed after deployment
- Engineer and incident commander approved the change in Slack
- No retrospective PR or formal review occurred

Decide whether the emergency path was controlled. A mature answer should distinguish the need to restore service from the need for a documented, time-bounded exception and retrospective review.

### Sample C: restore test

- Daily backups report success
- Restore completed in 3 hours 20 minutes
- Business requirement says RTO 2 hours, RPO 24 hours
- Restored record count matched production snapshot
- No incident or remediation ticket was created for the missed RTO

Explain why "backup succeeded" and "recovery objective was met" are different claims.

## Part 5: Produce the mini assurance pack

Create these six outputs:

1. one-paragraph scope statement;
2. eight-row risk register;
3. eight-to-twelve-row control matrix;
4. a Statement of Applicability outline for ISO/IEC 27001, including why relevant controls are included or excluded;
5. a one-page management review note covering risk, incidents, objectives, audit findings, resources, and improvement actions;
6. a gap list ranked as critical, pre-audit, and later improvement.

For SOC 2, also write a short system description outline: services, infrastructure, software, people, procedures, data, boundaries, commitments, subservice organizations, and complementary user-entity controls.

## Exit criteria

You pass the lab if you can defend these points aloud:

- SOC 2 is a CPA attestation report; ISO/IEC 27001 is a certifiable management-system standard.
- Type 1 addresses a point in time; Type 2 adds operating effectiveness over a period.
- ISO/IEC 27001 certification is not granted by ISO. A competent certification body performs the audit, with accreditation providing confidence in that body's competence.
- ISO/IEC 27001 requires a functioning ISMS, risk treatment, internal audit, management review, corrective action, and continual improvement. Annex A is not a flat checklist to apply blindly.
- Evidence must demonstrate that a control operated for the population and period, not merely that a policy exists.
- A single well-designed control can map to SOC 2, ISO/IEC 27001, and NIST CSF 2.0, but the assurance expectations and terminology differ.

## Interview debrief

Prepare 90-second answers for:

1. How would you get a small SaaS company ready for SOC 2?
2. What is the practical difference between SOC 2 and ISO/IEC 27001?
3. How do you prevent compliance work from becoming checkbox security?
4. An auditor finds one failed access-removal sample. What do you do?
5. How does DevSecOps produce compliance evidence?

Read `answer-key/README.md` after finishing.

