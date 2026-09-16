# Lab 3: Deploy and Harden a SaaS Workload on Kubernetes

## Objective

Deploy an intentionally over-privileged workload, identify its trust and privilege problems, then apply and verify Kubernetes controls without breaking the service.

This lab focuses on workload and namespace security. A real managed cluster also requires secure control-plane configuration, private endpoints, node hardening, cloud IAM, secret encryption, audit logging, patching, admission governance, and tenant isolation.

## What you should learn

- The relationship between containers, Pods, Deployments, Services, namespaces, service accounts, RBAC, admission, and NetworkPolicy.
- Why a non-root container is useful but does not by itself secure a cluster.
- How Pod Security Admission, security contexts, RBAC, network controls, resource controls, image provenance, and observability layer together.
- How to verify a control rather than assuming a YAML object works.

## Setup

You need Docker, `kubectl`, `kind`, and a NetworkPolicy-capable CNI. The upstream Kubernetes documentation warns that a NetworkPolicy object has no effect unless the cluster's network plugin enforces it.

One local option is a kind cluster with Cilium. Install the Cilium CLI using its official instructions, then run:

```bash
kind create cluster --name invoiceflow --config starter/kind-cluster.yaml
cilium install
cilium status --wait
kubectl cluster-info --context kind-invoiceflow
```

If you already have a disposable cluster with a NetworkPolicy-capable CNI, use that instead.

## Concept refresh

| Object | Practical purpose | Common security mistake |
| --- | --- | --- |
| Container | Packaged process and filesystem | Root process, broad capabilities, writable root filesystem, untrusted image |
| Pod | Smallest scheduled unit; one or more containers share network and selected namespaces | Treating it as a strong tenant boundary |
| Deployment | Maintains replicas and rollout state | Mutable tags, no probes, no resource settings, unsafe rollout |
| Service | Stable virtual endpoint for selected Pods | Unnecessary public or node-wide exposure |
| Namespace | Organizational and policy scope | Assuming it is automatically a hard isolation boundary |
| ServiceAccount | Workload identity inside Kubernetes | Default account and unnecessary API token mounting |
| RBAC | API authorization | Wildcards, cluster-wide bindings, granting workload creation as though it were low risk |
| Admission | Validates or mutates objects before persistence | Relying on developer intent with no enforced baseline |
| NetworkPolicy | Layer 3/4 Pod traffic allow-list when enforced by the CNI | Creating policy on a CNI that ignores it, or forgetting DNS/required egress |

## Part 1: Deploy and inspect the weak workload

```bash
kubectl apply -f starter/insecure-workload.yaml
kubectl -n invoiceflow rollout status deployment/invoiceflow-api
kubectl -n invoiceflow get all
kubectl -n invoiceflow get pod -l app=invoiceflow-api -o yaml
```

List at least ten weaknesses. Include:

- privileged container;
- root user and privilege escalation;
- default seccomp behavior not explicitly constrained;
- service-account token mounted despite no API requirement;
- default service account;
- no resource requests or limits;
- no readiness/liveness/startup behavior;
- NodePort exposure;
- no network isolation;
- mutable image reference;
- no Pod Security Admission enforcement;
- no spread or disruption considerations;
- no evidence of image signing/attestation or admission verification.

Inspect effective identity and token mounting:

```bash
POD=$(kubectl -n invoiceflow get pod -l app=invoiceflow-api -o jsonpath='{.items[0].metadata.name}')
kubectl -n invoiceflow exec "$POD" -- id
kubectl -n invoiceflow exec "$POD" -- sh -c 'test -f /var/run/secrets/kubernetes.io/serviceaccount/token && echo token-mounted'
```

Explain why permission to create a Pod or Deployment can become an indirect privilege-escalation route even when the principal cannot directly read Secrets: a workload can request service accounts, volumes, host access, or other powerful settings unless admission and RBAC constrain it.

## Part 2: Add an enforced workload baseline

Delete the weak namespace, then apply the solution namespace and workload:

```bash
kubectl delete namespace invoiceflow
kubectl apply -f solution/namespace.yaml
kubectl apply -f solution/workload.yaml
kubectl -n invoiceflow rollout status deployment/invoiceflow-api
```

The namespace enforces the Restricted Pod Security Standard. The hardened workload should include:

- a dedicated service account;
- `automountServiceAccountToken: false`;
- `runAsNonRoot: true` and a non-zero UID/GID;
- `allowPrivilegeEscalation: false`;
- all Linux capabilities dropped;
- `seccompProfile.type: RuntimeDefault`;
- read-only root filesystem;
- explicit CPU/memory requests and limits;
- readiness and liveness probes;
- ClusterIP-only exposure;
- multiple replicas and a conservative rolling update.

Prove admission enforcement by trying the original manifest again:

```bash
kubectl apply -f starter/insecure-workload.yaml
```

Expected result: the namespace already exists and the privileged Pod template should be rejected by the Restricted policy. Read the admission error and connect each failure to a security-context field.

## Part 3: Restrict Kubernetes API permissions

Apply the example role:

```bash
kubectl apply -f solution/rbac.yaml
kubectl auth can-i get pods -n invoiceflow --as=interviewer@example.com
kubectl auth can-i get pods/log -n invoiceflow --as=interviewer@example.com
kubectl auth can-i create deployments -n invoiceflow --as=interviewer@example.com
kubectl auth can-i get secrets -n invoiceflow --as=interviewer@example.com
```

Expected answers: yes, yes, no, no.

Review the role and answer:

- Why is it namespace-scoped instead of a ClusterRoleBinding?
- Why are `secrets`, `pods/exec`, `serviceaccounts/token`, `roles`, and `rolebindings` excluded?
- Why can `create pods` or `create deployments` be much more powerful than it appears?
- Would support staff need all Pod logs, or should application-level tooling expose a narrower view?

## Part 4: Enforce and test east-west traffic

Apply the two client Pods and network policies:

```bash
kubectl apply -f solution/clients.yaml
kubectl apply -f solution/network-policy.yaml
kubectl -n invoiceflow wait --for=condition=Ready pod/allowed-client pod/rogue-client --timeout=90s
SERVICE_IP=$(kubectl -n invoiceflow get service invoiceflow-api -o jsonpath='{.spec.clusterIP}')
kubectl -n invoiceflow exec allowed-client -- curl -fsS --max-time 5 "http://${SERVICE_IP}:8080/hostname"
kubectl -n invoiceflow exec rogue-client -- curl -fsS --max-time 5 "http://${SERVICE_IP}:8080/hostname"
```

Expected result:

- `allowed-client` succeeds because its label matches the explicit ingress and egress policies.
- `rogue-client` times out or fails because default-deny applies and it has no allow rule.

If both clients succeed, do not edit YAML blindly. Verify that the CNI enforces NetworkPolicy, inspect labels/selectors, and confirm the policies select the intended Pods.

Also verify the API has no unnecessary egress:

```bash
kubectl -n invoiceflow get networkpolicy
kubectl -n invoiceflow describe networkpolicy
```

In a real SaaS deployment, allow only required flows such as API-to-database, metrics-to-scraper, and carefully scoped DNS or external service egress. Kubernetes NetworkPolicy is primarily Layer 3/4 and is not a replacement for application authorization, mTLS identity, or Layer 7 policy.

## Part 5: Supply chain and secret design

Write a production design for these gaps:

1. resolve image tags to immutable digests;
2. generate an SBOM during the build;
3. sign/attest the image and verify it at admission;
4. allow deployment only from the trusted registry;
5. scan continuously because new vulnerabilities appear after deployment;
6. obtain secrets from a managed secret store using workload identity;
7. avoid storing plaintext secrets in Git or broad ConfigMaps;
8. collect Kubernetes audit, admission, workload, identity, and network telemetry;
9. define patching and exception SLAs;
10. separate production deployment authority from routine development access.

Explain an important nuance: a Kubernetes Secret is an API object for handling secret data, but base64 encoding is not encryption. Protect Secrets with encryption at rest, restricted RBAC, transport security, careful projection, rotation, and preferably external secret management or workload identity where appropriate.

## Part 6: Diagnose a failed hardening change

Assume `readOnlyRootFilesystem: true` causes a new release to crash because a third-party library writes under `/tmp`.

Show the response:

1. inspect events, container status, previous logs, and effective manifest;
2. identify the required writable path;
3. mount a size-limited `emptyDir` only at that path;
4. preserve the read-only root filesystem;
5. verify startup, legitimate writes, resource behavior, and cleanup;
6. document why disabling the entire restriction would be broader than required.

This is a common interview pattern: preserve the security objective while making the minimum compatible change.

## Exit criteria

You pass when:

- Restricted Pod Security Admission rejects the insecure workload;
- the hardened service remains healthy;
- the workload does not run as root or receive a service-account token;
- the log reader can read Pod logs but cannot deploy workloads or read Secrets;
- the allowed network flow succeeds and the rogue flow fails;
- you can name the controls still owned by the cloud provider, cluster platform team, application team, and security team.

## Interview debrief

Prepare 90-second answers for:

1. How would you secure a Kubernetes-hosted SaaS product?
2. What is the difference between RBAC, Pod Security Admission, and NetworkPolicy?
3. Why is a namespace not automatically a security boundary?
4. How would you handle secrets and workload identity?
5. A hardening control breaks production. How do you respond without simply disabling it?

## Cleanup

This deletes only the disposable cluster named `invoiceflow`:

```bash
kind delete cluster --name invoiceflow
```

