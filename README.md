# SaaS Security Interview Labs

Three focused labs for refreshing compliance, AppSec/DevSecOps, and Kubernetes security in a realistic SaaS environment.

## The shared scenario

You have joined **InvoiceFlow**, a 35-person B2B SaaS company. Customers upload invoices, assign them to employees, and export financial reports.

- The product is a Python API deployed as a container to Kubernetes.
- Customer data includes names, email addresses, invoice amounts, and free-text notes.
- GitHub hosts source code and CI/CD.
- A managed cloud database stores production data.
- Entra ID is the workforce identity provider.
- The company wants larger customers and has been asked for a SOC 2 report and ISO/IEC 27001 certification.
- There is one security engineer, a small platform team, and no mature GRC program.

The three labs deliberately connect:

1. Define the risks and controls the SaaS business claims to operate.
2. implement some of those controls in code and CI/CD.
3. implement and test the runtime controls in Kubernetes.

## Recommended sequence

| Lab | Time | Main output | Interview skill |
| --- | ---: | --- | --- |
| 1. SOC 2 + ISO/IEC 27001 | 90-120 min | Scope, risk register, control matrix, evidence review | Explain compliance as an operating system, not a checklist |
| 2. AppSec + DevSecOps | 90-120 min | Threat model, code fixes, CI security gates, exception decision | Explain how security fits into delivery without blocking every release |
| 3. Kubernetes security | 90-150 min | Hardened workload, RBAC, Pod Security Admission, NetworkPolicy tests | Explain Kubernetes trust boundaries and prove controls work |

Do the labs before reading each answer key. The goal is not to memorize framework wording. The goal is to explain the risk, control, evidence, failure mode, and tradeoff.

## Prerequisites

Required for Lab 2:

- Git
- Docker
- Python 3.11+

Required for Lab 3:

- Docker
- `kubectl`
- `kind`
- Internet access to pull images and install a NetworkPolicy-capable CNI

Optional tools:

- Semgrep
- Gitleaks
- Trivy
- Syft
- Checkov or Kubescape

## Fast interview model

Use this chain when answering design questions:

`business objective -> risk -> control -> implementation -> evidence -> test -> exception/remediation`

Example:

> The risk is unauthorized production change. We require pull-request review and protected branches, enforce it in GitHub, retain PR and deployment records as evidence, sample changes during assurance work, and document emergency-change exceptions with retrospective approval.

That answer is stronger than listing framework control IDs because it explains how the control operates.

## Key distinctions to retain

| Topic | Practical meaning |
| --- | --- |
| SOC 2 | An independent CPA attestation report about controls relevant to selected Trust Services Criteria. It is not a certification. |
| SOC 2 Type 1 | Design and implementation of controls at a point in time. |
| SOC 2 Type 2 | Design and operating effectiveness over a review period. |
| ISO/IEC 27001 | Requirements for an information security management system, or ISMS. An accredited certification body can certify the organization against it. |
| NIST CSF 2.0 | A flexible outcome framework for understanding and improving cybersecurity risk. It does not itself create an attestation report or certification. |
| AppSec | Security of the product and its design, code, dependencies, and behavior. |
| DevSecOps | Integration of security work and feedback into development and operations workflows. It is an operating approach, not a scanner bundle. |
| Container | A packaged process with isolated filesystem, namespaces, and resource controls, while sharing the host kernel. |
| Kubernetes | An orchestrator that schedules and manages workloads. Its API, admission, identity, networking, workload configuration, nodes, and supply chain are separate security surfaces. |

## Source notes

This pack uses the current published ISO/IEC 27001 edition, ISO/IEC 27001:2022, including its published 2024 amendment. It references but does not reproduce the copyrighted standard. SOC 2 terminology follows AICPA material. AppSec tasks are aligned to NIST SSDF and OWASP verification practices. Kubernetes tasks follow the upstream security checklist, application security checklist, Pod Security Standards, RBAC, and NetworkPolicy documentation.

Primary references:

- ISO, [ISO/IEC 27001:2022 overview](https://www.iso.org/standard/27001)
- AICPA, [SOC suite of services](https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services)
- AICPA, [Trust Services Criteria](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022)
- NIST, [SP 800-218 Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)
- OWASP, [Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)
- Kubernetes, [Security checklist](https://kubernetes.io/docs/concepts/security/security-checklist/)
- Kubernetes, [Application security checklist](https://kubernetes.io/docs/concepts/security/application-security-checklist/)
- Kubernetes, [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- Kubernetes, [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

