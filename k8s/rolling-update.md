# Rolling update and rollback (Task 3)

These commands assume the manifests in this folder are applied to a cluster (for example Minikube).

```bash
# Deploy
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl rollout status deployment/devops-case-study-app

# Rolling update to a new image tag
kubectl set image deployment/devops-case-study-app \
  app=bishwajeets11/devops-case-study-app:v2.0.0
kubectl rollout status deployment/devops-case-study-app
kubectl rollout history deployment/devops-case-study-app

# Rollback to the previous revision
kubectl rollout undo deployment/devops-case-study-app
kubectl rollout status deployment/devops-case-study-app
kubectl get pods -l app=devops-case-study-app
```

Strategy in `deployment.yaml`:

- `type: RollingUpdate`
- `maxSurge: 1` (one extra pod during the update)
- `maxUnavailable: 0` (do not take healthy pods down first)
