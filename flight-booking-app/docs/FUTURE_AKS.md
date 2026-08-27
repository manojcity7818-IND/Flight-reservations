# Future AKS deployment (not implemented in this change)

This document only describes the intended production shape. There are **no** Kubernetes manifests, Helm charts, Ingress objects, Application Gateway configs, or Terraform changes in this repository yet.

```
                    Internet
                       |
                       v
              Azure Application Gateway
                       |
          +------------+------------+------------+
          |                         |            |
       /hotels                   /flights       /cab
          |                         |            |
          v                         v            v
 Existing Hotel App        Flight Booking App   Future Cab App
                                  |
                         +--------+--------+--------+
                         |        |        |        |
                         v        v        v        v
                      Flight   Booking  Payment  Notification
                      Search   Service  Service  Service
                         |
                         v
                    Mock flight data
```

Path-based routing (later):

- `/hotels` → existing Hotel Reservation application
- `/flights` → this My Booking flight application (frontend + API gateway)
- `/cab` → a future cab application

Suggested later steps (not done now):

1. Push images from CI to Azure Container Registry using service connections / variable groups.
2. Deploy each microservice as its own Deployment + Service in AKS.
3. Keep the API gateway as the single in-cluster entry for `/flights/api/*`.
4. Front the cluster with Application Gateway (or AGIC / Gateway API) for `/hotels` and `/flights`.
5. Add CD pipelines only after the apps are stable.
