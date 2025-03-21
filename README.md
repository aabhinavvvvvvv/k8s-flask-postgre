# Kubernetes Flask PostgreSQL Dashboard

This project demonstrates how to:
1. Create a Kubernetes namespace.
2. Provision a Flask app and PostgreSQL database in the namespace.
3. Automatically fetch and store running pod names in the PostgreSQL database.

---

## **Prerequisites**
- Kubernetes cluster (e.g., Minikube, Kind, or a cloud-based cluster)
- Docker
- kubectl
- Python 3.x

---

## **Setup**

### **1. Clone the Repository**
Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/kubernetes-flask-postgres.git
cd kubernetes-flask-postgres
```


### **2. Apply Kubernetes Manifests**
Apply the Kubernetes manifests to create the namespace, pods, and services.

#### **Create the Namespace**
Create the `nrp` namespace:

```bash
kubectl apply -f namespace.yaml
```

#### **Deploy the PostgreSQL Database**
Deploy the PostgreSQL pod and service:

```bash
kubectl apply -f postgres-pod.yaml
kubectl apply -f postgres-service.yaml
```

#### **Deploy the Flask App**
Deploy the Flask app pod and service:

```bash
kubectl apply -f flask-pod.yaml
kubectl apply -f flask-service.yaml
```

#### **Set Up RBAC (Role-Based Access Control)**
Grant the Flask app permission to list pods in the `nrp` namespace:

```bash
kubectl apply -f pod-reader-role.yaml
kubectl apply -f pod-reader-rolebinding.yaml
```

### **3. Access the Flask App**
Use `kubectl port-forward` to access the Flask app locally.

#### **Port Forwarding**
Forward port 5000 from the `flask-app` pod to your local machine:

```bash
kubectl port-forward pod/flask-app -n nrp 5000:5000
```

#### **Test the `/pods` Endpoint**
Fetch the list of running pods:
You can also use Postman to test this route after port forwarding
This route does not give us pods that we store in our database through store-pods..This only gives the list of running pods on our namespace..This is because we can store pods in our databse that might not even be running on our namespace...
```bash
curl http://localhost:5000/pods
```

**Expected Response:**

```json
["flask-app", "postgres-db"]
```

#### **Test the `/store-pods` Endpoint**
Before doing this first create table:
```bash
kubectl exec -it postgres-db -n nrp -- psql -U admin -d nrp_db
CREATE TABLE pods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
\dt
```
Store pod names in the PostgreSQL database:
You can also use postman for this
```bash
curl -X POST http://localhost:5000/store-pods -H "Content-Type: application/json" -d '{"pod_names": ["flask-app", "postgres-db"]}'
```

**Expected Response:**

```json
{"message": "Pod names stored successfully"}
```

### **4. Verify Data in PostgreSQL**
Connect to the PostgreSQL pod and query the `pods` table to confirm the data was stored.

#### **Connect to PostgreSQL**

```bash
kubectl exec -it postgres-db -n nrp -- psql -U admin -d nrp_db
```

#### **Query the `pods` Table**

```sql
SELECT * FROM pods;
```

**Expected Output:**

```
 id |    name
----+------------
  1 | flask-app
  2 | postgres-db
(2 rows)
