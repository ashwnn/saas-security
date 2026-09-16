# Lab 2: Secure a SaaS Pull Request and Delivery Pipeline

## Objective

Review and repair a deliberately weak InvoiceFlow API, then design CI/CD security gates that give developers fast feedback without treating every scanner result as release-blocking.

Run the vulnerable service only on your own machine. All credentials and data are synthetic.

## What you should learn

- Threat modeling a small feature by identifying assets, actors, entry points, trust boundaries, and abuse cases.
- Distinguishing SAST, SCA, secret scanning, container scanning, IaC scanning, DAST, tests, and runtime defenses.
- Fixing root causes instead of merely suppressing findings.
- Designing gates around exploitability, severity, confidence, asset context, and approved exceptions.
- Producing useful evidence for compliance controls from normal engineering work.

## Setup

```bash
cd lab-2-appsec-devsecops/starter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
flask --app app run --port 5000
```

In another shell:

```bash
curl -s http://127.0.0.1:5000/health
curl -s 'http://127.0.0.1:5000/invoices?customer=acme'
```

Do not expose the service to a public interface.

## Part 1: Create a compact threat model

Draw or write this data flow:

`browser/API client -> ingress -> InvoiceFlow API -> PostgreSQL/object storage`

Add these supporting paths:

- developer -> GitHub -> CI/CD -> registry -> cluster;
- support engineer -> admin export;
- API -> logs/monitoring;
- API -> third-party email service.

For each trust boundary, list:

- authentication and authorization decision;
- sensitive data crossing the boundary;
- validation or encoding requirement;
- secret or identity used;
- logging needed to investigate abuse;
- rate or resource limit.

Identify at least six abuse cases. Include tenant-boundary bypass, injection, stolen administrative credential, sensitive data in logs, malicious dependency, and tampered deployment artifact.

## Part 2: Review the starter code

Inspect:

- `app.py`
- `Dockerfile`
- `.github/workflows/ci.yml`
- `tests/test_app.py`

Find at least eight issues. Categorize each as design, code, dependency/supply chain, pipeline, container, configuration, or operational weakness.

Minimum expected findings:

1. SQL query construction accepts attacker-controlled input.
2. A synthetic administrative token is committed in source.
3. Administrative authorization depends on one static shared secret.
4. Detailed exception text is returned to clients.
5. Flask debug mode is enabled in the container.
6. The container runs as root and has no health check.
7. The pipeline runs tests but no security checks.
8. Action references use moving major tags rather than immutable commit SHAs.
9. There is no tenant-aware authorization model.
10. There is no rate limit or security event logging for admin export.

The point is not that every item must be solved in this small PR. Decide what blocks release, what requires a design change, and what can be tracked with a bounded exception.

## Part 3: Exploit safely and write regression tests

Demonstrate the injection against the local instance:

```bash
curl -sG http://127.0.0.1:5000/invoices \
  --data-urlencode "customer=' OR 1=1 --"
```

Expected vulnerable behavior: invoices belonging to more than one customer are returned.

Before fixing the code, add a test asserting that the same input returns no other customer's records. Also test:

- normal customer lookup still works;
- a missing admin secret fails closed;
- an invalid admin credential returns 401 without disclosing the expected value;
- exception responses do not expose raw internal error text.

## Part 4: Fix the implementation

Implement at least these changes:

- use parameterized SQL;
- load the administrative secret from the environment and fail closed when it is not configured;
- use constant-time comparison for the synthetic shared-secret check;
- return a generic client error and log a server-side event without sensitive data;
- disable debug mode;
- run the image as a non-root user;
- add a container health check;
- add a `.dockerignore` that excludes `.git`, virtual environments, caches, tests if they are not required, and local secrets.

Then document the architectural limitation: a shared admin secret is not an acceptable long-term production identity model. Recommend workload/user identity, short-lived credentials, role-based authorization, tenant-scoped queries, and audited privileged operations.

Compare your changes with `solution/` only after you finish.

## Part 5: Add proportionate pipeline gates

Design a pipeline with this order:

1. unit and security regression tests;
2. secret scanning over repository history and changed content;
3. SAST;
4. dependency/SCA scan;
5. build the container once;
6. scan that exact image;
7. generate an SBOM;
8. sign or attest the image in a production design;
9. deploy the same immutable digest, not a rebuilt image;
10. run a post-deployment smoke test and retain deployment evidence.

Suggested local checks:

```bash
semgrep --config=p/python --config=p/owasp-top-ten --error .
gitleaks detect --source . --no-banner
trivy fs --scanners vuln,secret,misconfig .
docker build -t invoiceflow:lab .
trivy image --severity HIGH,CRITICAL invoiceflow:lab
```

Scanner output changes over time. Record tool version, ruleset/database timestamp, command, commit SHA, and artifact digest so the result is reproducible.

Your gate policy should answer:

- Does a verified secret always block?
- Do new critical or high vulnerabilities block? Under what exploitability and fix-availability rules?
- How are existing findings baselined without hiding regression?
- Who can approve an exception?
- What evidence and expiry are required?
- What happens when a scanner is unavailable?

A practical starting policy:

- block verified secrets and exploitable injection/authentication failures;
- block new critical vulnerabilities in a reachable production component;
- block high findings when exploitability and asset context justify it;
- warn on lower-confidence or lower-severity findings and create owned work;
- require a time-bounded exception with compensating controls for an intentional bypass;
- do not silently pass a security job that failed to execute.

## Part 6: Triage a real release decision

Assume a Friday release fixes invoice corruption. The image scanner reports a High CVE in an OS library:

- no fixed package is available;
- the vulnerable function is not called by the application;
- the container is internet-facing;
- exploitability analysis is incomplete;
- the release fixes an active data-integrity incident.

Write a one-page decision with:

1. technical finding and uncertainty;
2. business impact of delaying the fix;
3. reachability/exploitability analysis;
4. compensating controls;
5. approver;
6. expiry date and retest trigger;
7. rollback and monitoring;
8. permanent remediation owner.

There is no automatic "correct" answer. A strong answer makes the risk owner, time boundary, evidence, and monitoring explicit.

## Exit criteria

You pass when:

- tests prove the injection no longer crosses customer boundaries;
- no secret is stored in source;
- the image runs as non-root;
- the pipeline contains distinct tests for code, dependencies, secrets, image, and deployment integrity;
- failures have defined block/warn/exception behavior;
- you can explain why a scanner is a detective control and why secure design, review, tests, identity, and runtime restrictions are still needed.

## Interview debrief

Prepare 90-second answers for:

1. What does DevSecOps mean in practice?
2. Where would you add security checks in CI/CD?
3. How do you prevent scanners from overwhelming developers?
4. How would you secure software supply-chain artifacts?
5. How does this pipeline support SOC 2 or ISO/IEC 27001 evidence?

