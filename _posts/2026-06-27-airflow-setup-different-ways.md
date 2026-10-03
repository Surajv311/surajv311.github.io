---
layout: post 
title: Setting up Airflow (and other OSS) - Past vs Today
category: technicalArticles
---

> From my experience working at [GreyOrange](https://www.greyorange.com/). Refactored my article a bit with help of GPT. 

I had the fortune of working in data teams of different companies, and one thing that I noticed is the evolution of setting up OSS (open-source software) on cloud.  

> Tldr; From VMs to Docker to Helm-Kubernetes

For instance, let's talk about [Airflow](https://github.com/apache/airflow). Apache Airflow is an open-source workflow orchestration platform. You define data pipelines as DAGs (Directed Acyclic Graphs) in Python — each DAG describes what tasks to run, in what order, and on what schedule. Airflow handles scheduling, execution, retries, logging, and a web UI for visibility.

It has a few core components like scheduler, workers, webserver/apiserver, etc.

When setting up for the first time on cloud - the deployment model for all these components have changed over years. I would divide it as: 

1) VM era:

Teams would spin up one or more virtual machines and install Airflow directly on the OS.

```bash
# Typical setup steps on Ubuntu/Debian
sudo apt-get install python3-pip
pip install apache-airflow
export AIRFLOW_HOME=~/airflow
airflow db init
airflow users create --username admin --role Admin ...
airflow webserver --port 8080 &
airflow scheduler &
```

Workers would be started similarly, either on the same machine or additional VMs. The metadata database (Postgres) was either installed on the same VM or pointed to an external managed instance.

Managing looked like: 
- DAGs were deployed by SSHing into the VM and copying `.py` files into `$AIRFLOW_HOME/dags/`
- Dependencies were installed with `pip install` directly on the VM, shared across all DAGs
- Config changes required editing `airflow.cfg` and restarting processes via `systemctl` or screen sessions
- Scaling workers meant provisioning a new VM, installing everything again manually, and hoping nothing drifted
- Upgrades were painful: `pip install --upgrade apache-airflow` could break existing DAGs or dependencies

Pros: 
- **Simple mental model** — it's just a process on a server
- **No container or orchestration knowledge required**
- **Easy to debug**: SSH in, look at logs, check processes

Cons: 
- **No isolation**: all DAGs share the same Python environment; one DAG's `pip install` can break another's
- **Manual scaling**: adding a worker means provisioning and configuring a new VM by hand
- **Config drift**: servers diverge over time; "works on my VM" is a real problem
- **No HA out of the box**: if the scheduler process crashes, nothing restarts it automatically
- **Dependency hell**: conflicting package versions across DAGs are a constant headache
- **Upgrades are risky**: a bad `pip upgrade` can take down the entire Airflow installation

2) Container era:

The era of Docker came. Instead of installing Airflow on a host OS, you'd pull (or build) a Docker image containing Airflow and all its dependencies, then run it as a container.

```dockerfile
# Custom Airflow image with extra packages
FROM apache/airflow:3.x.x
RUN pip install pandas boto3 google-cloud-bigquery
COPY dags/ /opt/airflow/dags/
```

```bash
# Running Airflow webserver in Docker
docker run -d \
  -p 8080:8080 \
  -e AIRFLOW__CORE__EXECUTOR=LocalExecutor \
  -e AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow \
  -v $(pwd)/dags:/opt/airflow/dags \
  apache/airflow:3.x.x webserver
```
Airflow project provided an official `docker-compose.yaml` as well to run entire stack. 

Managing looked like: 

- DAGs were mounted as a volume into the container, or baked into a custom Docker image
- Custom dependencies went into a custom `Dockerfile` extending the base Airflow image
- Config was passed as environment variables (`AIRFLOW__SECTION__KEY=value`)
- Scaling meant increasing container replicas on a host; scaling across machines required additional orchestration
- Upgrades meant pulling a new image tag and running `docker-compose up -d`

Pros: 
- **Reproducibility**: same image runs the same way on any machine
- **Isolation**: Airflow's Python environment is sealed inside the container
- **Easier upgrades**: swap image tags, rebuild, redeploy
- **Local dev**: any engineer can run the full Airflow stack on their laptop with `docker-compose up`
- **Simpler dependency management**: pip installs go into the Dockerfile, not the host

Cons: 
- **Still manual scaling**: docker-compose is single-host; scaling across machines requires extra tooling (Docker Swarm, or moving to Kubernetes)
- **Not production-grade HA**: docker-compose has no self-healing, no rolling restarts, no health-based rescheduling
- **DAG deployment is still a concern**: you either remount volumes (operational complexity) or rebuild and redeploy images (slow CI loop)
- **No cloud-native integration**: no automatic secrets injection, no auto-scaling, no native logging to cloud log sinks
- **CeleryExecutor needs MessageBroker**: Like RabbitMQ/Redis extra service to manage and keep healthy

3) K8s era: 

We can now setup Airflow using helm charts on K8s. K8s provides:
- **Self-healing:** crashed containers are automatically restarted
- **Horizontal scaling:** add more pods with a single command or HPA rule
- **Rolling deployments:** update with reduced deployment downtime
- **Resource management:** CPU and memory limits per component
- **Native secrets/config management:** Kubernetes Secrets and ConfigMaps
- **Cloud integration:** persistent volumes, load balancers, IAM, logging — all first-class

But deploying a complex multi-component application like Airflow on Kubernetes by hand (writing Deployments, Services, PVCs, ConfigMaps, Secrets for each component) is repetitive and error-prone. That's where **Helm** comes in. Helm is the package manager for Kubernetes. A **Helm chart** is a collection of templated Kubernetes manifests packaged together with configurable values.

We can think of it like `apt` or `pip` but for Kubernetes applications.

```bash
# Install Airflow on Kubernetes with Helm
helm repo add apache-airflow https://airflow.apache.org
helm install airflow apache-airflow/airflow \
  --namespace airflow \
  --create-namespace \
  -f values.yaml
```

One command which you could run from a bastion machine that has access to the K8s namespace and Airflow's entire stack — scheduler, webserver, workers, triggerer, metadata DB connection, ingress, RBAC — deployed on that namespace.

Notice in the command, we are passing a `values.yaml` file, it basically has our complete Airflow deployment config, it may look like below for example: 

```yaml
# Airflow image — use official or custom
images:
  airflow:
    repository: your-registry/custom-airflow
    tag: "3.x.x"
    pullPolicy: IfNotPresent

# Executor choice
executor: KubernetesExecutor   # or CeleryExecutor, LocalExecutor

# Webserver
webserver:
  replicas: 2
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"

# Scheduler
scheduler:
  replicas: 1
  resources:
    requests:
      memory: "2Gi"
      cpu: "1000m"

# Workers (CeleryExecutor)
workers:
  replicas: 3
  resources:
    requests:
      memory: "4Gi"
      cpu: "2000m"

...Similarly database, env variables, and other details... 
```

There are 3 common patterns to deploy/update DAGs via helm: 
- Git-sync sidecar: A sidecar container runs alongside the scheduler and workers, continuously polling a Git repo and syncing DAGs to a shared volume. No manual file copying, no image rebuilds for DAG changes.
- GCS bucket mounted via GKE FUSE (Cloud-native alternative): On GKE (Google K8s), you can mount a Google Cloud Storage bucket directly into Airflow pods as a filesystem using **GCSFuse** (via the GKE Cloud Storage FUSE CSI driver). DAGs live in GCS, are mounted at `/opt/airflow/dags` inside the pod, and updates to the bucket are visible to pods without any restart or re-sync delay generally. You could sync DAGs to GCS buckets via any simple CI pipeline.
- Bake DAGs into custom image: Build a custom Docker image that includes your DAGs. Every DAG change requires a new image build and Helm upgrade. Slower iteration but more reproducible.

Similarly, upgrading airflow via helm is simple as well. 

Pros: 
- **Self-healing:** Kubernetes restarts crashed pods automatically
- **Rolling updates:** zero-downtime upgrades via Helm upgrade
- **GitOps-friendly:** `values.yaml` in Git; CD pipelines trigger `helm upgrade`
- **Per-task isolation:** KubernetesExecutor gives each task its own pod and Python environment
- **Auto-scaling:** HPA can scale workers based on external/custom metrics
- **Cloud-native:** native secrets, PVCs, service accounts, IAM integration
- **Resource governance:** CPU/memory limits per component prevent one runaway DAG from killing the scheduler
- **Multi-environment parity:** same Helm chart, different `values.yaml` per env (dev/staging/prod)

Cons: 
- **Kubernetes knowledge required:** your team must understand pods, PVCs, RBAC, ingress
- **Complexity of values.yaml:** the official Airflow Helm chart has hundreds of configurable values
- **Cold start latency (KubernetesExecutor):** each task (if using K8sExecutor) incurs pod scheduling latency (~5–30s) vs. a warm Celery worker
- **Spot/preemptible nodes need care:** if the scheduler pod is on a Spot node, eviction causes a brief scheduling pause — use node affinity or priority classes to keep the scheduler on stable nodes
- **Log management:** logs are ephemeral in pods; must configure remote logging (GCS, S3, Elasticsearch) from day one

Hence, for teams setting up OSS Airflow rather than using any managed service, helm is preffered way. Note that a lot of other OSS like say: Superset, Trino, Metabase, their helm charts exist as well, and can be setup similarly.  

-----------------
