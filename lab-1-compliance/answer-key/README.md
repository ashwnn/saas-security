# Lab 1 Answer Key and Review Notes

## A defensible initial scope

The ISMS and SOC 2 system boundary should cover the InvoiceFlow SaaS service, the people and processes that develop and operate it, GitHub and CI/CD, the container registry, Kubernetes production environment, managed database, object storage, monitoring, Entra ID, support workflows that handle customer data, and critical vendors. Corporate systems can be excluded only where the exclusion is explicit and does not undermine in-scope controls. For example, payroll may be out of scope, but the HR process that triggers access removal is not.

Start SOC 2 with Security. Include Availability only if management's uptime and recovery commitments are defined and the supporting controls actually operate. Confidentiality may also be justified because invoice data and notes are contractually restricted. More categories do not automatically make the report better.

## Sample A

Likely classification: an operating exception and possibly a design weakness.

- The Entra step worked on time.
- The GitHub removal was 15 days late.
- The ticket's broad claim was unsupported because it did not cover GitHub.
- If the procedure relies on a manual checklist with no authoritative downstream inventory, the control design is also weak.
- Investigate whether the contractor accessed code during the exposure window. Remove access, record the exception, correct the workflow, and verify similar departures.

Do not jump from one exception to "the entire program failed." Determine population, cause, duration, risk, compensating controls, and whether the issue is isolated or systemic.

## Sample B

The operational decision to restore service may be reasonable, but the emergency-change control did not fully operate if its defined procedure requires retrospective review. Slack approval and passing tests are useful evidence, but they do not replace an approved exception path. Create the retrospective change record, examine the outage and security impact, and fix enforcement or procedure ambiguity.

## Sample C

The backup control produced recoverable data and met the RPO, but recovery missed the stated RTO. The absence of a remediation ticket is a second weakness because management did not formally treat the failure. The correct response is to record the failed objective, analyze restore bottlenecks, assign corrective action, retest, and reconsider the business requirement only through an approved risk and business process.

## Strong gap order

Critical now:

- Remove orphaned access and examine exposure.
- Enforce MFA and privileged-access controls.
- Establish an incident path and ownership.
- Confirm backups are restorable and address the missed RTO.

Before an examination or certification audit:

- Approve scope, risk methodology, risks, control owners, ISMS objectives, policies, and exception paths.
- Enable consistent branch protection and evidence retention.
- Create vulnerability SLAs and time-bound risk acceptance.
- Inventory and tier vendors.
- Run an internal audit and management review for ISO/IEC 27001.
- Operate controls long enough to support the intended SOC 2 Type 2 period.

Later maturity:

- Automate identity and evidence collection.
- Improve control metrics and continuous monitoring.
- Expand Trust Services Categories only when customer commitments and risk justify it.

## Relationship to NIST CSF 2.0

Your NIST CSF experience transfers well:

- CSF Govern and Identify work becomes inputs to ISMS context, governance, risk assessment, and treatment.
- Protect, Detect, Respond, and Recover outcomes become control objectives and operating practices.
- SOC 2 and ISO/IEC 27001 add specific assurance mechanics, scope language, ownership, evidence, review, and independent examination/certification expectations.

The key change in mindset is moving from "we plan to improve this outcome" to "management asserts this control is designed and operating, and here is repeatable evidence."

