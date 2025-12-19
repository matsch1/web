---
title: "Nextcloud K3S deployment using helm chart"
slug: "nextcloud-k3s-helm-deployment"
date: 2025-12-19
description: "The way I deployed nextcloud on my k3s cluster using helm chart"
ShowToc: true
TocOpen: true
draft: false
cover:
  image: "nextcloud-k3s-helm-deployment.png"
  alt: "nextcloud-k3s-helm-deployment"
  caption: "The way I deployed nextcloud on my k3s cluster using helm chart"
  relative: true
tags:
  - kubernetes
  - k3s
  - nextcloud
---

## Introduction
Nextcloud is a self-hosted collaboration platform that provides file synchronization and sharing, calendars, contacts, and a growing ecosystem of apps. It offers strong data ownership guarantees while still covering many use cases typically handled by managed cloud services.
So my goal is to replace Google Drive, Contacs and Calendar with a self-hosted nextcloud instance.

In my homelab, I run a lightweight Kubernetes distribution based on k3s. 
To keep the deployment reproducible, maintainable, and aligned with cloud-native best practices, I decided to deploy Nextcloud using its Helm chart rather than relying on ad-hoc manifests or manual container setups. 
Helm allows me to describe the desired state declaratively, manage upgrades more safely, and keep configuration changes version-controlled.
This is the first step to go to manage my K3S cluster using Argo CD.

During the deployment process, I ran into several non-obvious challenges and application-specific configuration details that are easy to overlook when running Nextcloud on Kubernetes. 
This article documents the approach I took, the problems I encountered, and the solutions that worked for my k3s environment, with the goal of providing a practical reference for others attempting a similar setup.

## Helm Chart Setup
### Downloading the Helm Chart
The first step was to obtain the official Nextcloud Helm chart. Rather than installing it directly from the repository on every deployment, I prefer to download and vendor the chart locally. This gives me full visibility into the defaults, allows me to track changes over time, and avoids surprises when upstream defaults change.

``` sh
helm repo add nextcloud https://nextcloud.github.io/helm/
helm repo update
```

By keeping the chart alongside my cluster configuration, I can review updates deliberately and test them before rolling them out to my homelab.

### Values File Structure
The default `values.yaml` shipped with the chart is comprehensive but large. Modifying it directly quickly becomes unmaintainable, especially when comparing changes during upgrades.

To address this, I split the configuration into two files:

- `values-default.yaml`  
  This is the original `values.yaml`. It is not edited manually and serves as a reference for upstream changes.

- `values.yaml`  
  This file contains only my overrides and environment-specific configuration.

This approach has several advantages:

- Clear separation between upstream defaults and my customizations  
- Easier diffs when upgrading the chart  
- Reduced risk of accidentally diverging from intended defaults  

When deploying, both files are applied, with `values.yaml` overriding the defaults.


## Design Decisions
### Database Choice: SQLite First, MariaDB Later
For the initial deployment, I deliberately chose SQLite as the database backend. In a homelab context, this significantly reduces complexity:

- No additional database service to operate  
- Faster initial setup  
- Fewer moving parts while validating the deployment  

This decision was made with the explicit intention to migrate later. Once the deployment proved stable and usage increased, switching to MariaDB would be straightforward using the Helm chart’s database configuration options.

This staged approach allowed me to focus first on Kubernetes-specific concerns, and get familiar with Nextcloud, before introducing database operations and backups into the mix.

## Required Modifications
### Trusted Domains for Custom Domain Access
{{< figure src="https://help.nextcloud.com/uploads/default/original/3X/d/b/dbdf5a0e3ed2d78800f42f3612ef88c623e9ad8d.png" width="600" alt="Nextcloud untrusted domain error" >}}

Nextcloud is strict about which hostnames it accepts requests from. When running behind an ingress controller or a LoadBalancer, this becomes especially important.

I explicitly configured trusted domains to include:

The external domain exposed via ingress

Any internal service names used for testing or debugging

Without this configuration, Nextcloud may refuse connections or redirect users unexpectedly. Managing trusted domains through Helm values ensures the configuration persists across pod restarts and upgrades.

Add the following section to your `values.yaml` file:
``` yaml
nextcloud:
  trustedDomains: [localhost, <yourdomain.com>]
```

### Fixing the NextCloud App Store Connection
To install the Contacts and Calendar apps, Nextcloud needs to connect to the Nextcloud App Store. In my case, the App Store view was empty and failed to load content.

{{< figure src="https://forum.yunohost.org/uploads/default/original/2X/6/6c1ca5c9b3e6c1f5c36a7d64e700b0f8078f208e.png" width="600" alt="Nextcloud App Store connection error" link="https://forum.yunohost.org/t/nextcloud-appstore-does-not-work/30804" >}}

To identify the issue, I tested connectivity to the App Store both from the k3s node and from inside the Nextcloud container:
``` sh
curl https://apps.nextcloud.com
```

The request worked on the node but failed inside the container. After some debugging, I traced the issue to CoreDNS in the kube-system namespace.

This can be fixed by editing the CoreDNS ConfigMap:
``` sh
kubectl edit configMap coredns -nkube-system
```

Replace 
``` sh
forward . /etc/resolv.conf
``` 
with 
``` sh
forward . 1.1.1.1 8.8.8.8
```
.
This change mirrors the effective resolvers configured on the node. After applying it, the App Store loaded correctly and app installation worked as expected.

### DAV Configuration for Contacts and Calendar Access
I followed the guide by Robin to migrate my Google Contacts and Calendar to Nextcloud:
[Moving Google Contacts and Calendar to NextCloud](https://selfhostedheaven.com/posts/20220116-moving-google-contacts-and-calendar-to-nextcloud/)
During DAVx⁵ setup process I got stuck on `Grant Access` step.

{{< figure src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmZPWsy7ripvR1b7OIfdfyon23ykeLuhSVHA&s" width="400" alt="Nextcloud DAV Grant Access issue" link="https://itcamefromtheinternet.com/blog/nextcloud-android-sync/" >}}

To support DAV clients such as DAVx⁵, additional configuration is required. This is solved by injecting a custom configuration file via Helm values and enabling the HTTPS client fix.

``` yaml
nextcloud:
  configs:
    davx.config.php: |-
      <?php
      $CONFIG = array(
        'csrf.optout' => array(
          '/^WebDAVFS/',
          '/^Microsoft-WebDAV-MiniRedir/',
          '/RaiDrive/',
          '/CrKey/',
          '/Nextcloud-android/',
          '/Nextcloud-iOS/',
      ),
    );
  
│ phpClientHttpsFix:
│   enabled: true
│   protocol: https
```

After applying this configuration, the `Grant Access` step on my Android device worked without issues.

### Extra Manifests
Not everything fits cleanly into Helm values. For components that are adjacent to, but not strictly part of, the Nextcloud chart, I relied on extra manifests.

These manifests live alongside the Helm deployment and are applied as part of the same workflow. This keeps the overall deployment cohesive while still respecting the boundaries of the upstream chart.

In my case, I defined an external `LoadBalancer`` service:
``` yaml
│ extraManifests:
│   externalService:
│     apiVersion: v1
│     kind: Service
│     metadata:
│       name: nextcloud-external-service
│       namespace: nextcloud
│     spec:
│       type: LoadBalancer
│       selector:
│         app.kubernetes.io/component: app
│         app.kubernetes.io/instance: nextcloud
│         app.kubernetes.io/name: nextcloud
│       ports:
│         - protocol: TCP
│           port: 8080
│           targetPort: 80
│           nodePort: <nodePort>
```


## Deployment
With everything in place, deploying Nextcloud is straightforward:
``` sh
helm install nextcloud ./nextcloud \
  -n nextcloud \
  --create-namespace \
  -f ./nextcloud/values-default.yaml \
  -f ./nextcloud/values.yaml
```

## Summary
Deploying Nextcloud on a k3s cluster using Helm worked well, but it required more consideration than a simple helm install. By structuring configuration cleanly, making deliberate design decisions, and leveraging Helm features such as custom config files and extra manifests, I ended up with a setup that is both flexible and maintainable.

The next steps for this deployment include migrating to MariaDB, tightening security settings, and adding proper backup and monitoring workflows. Even in its current form, however, this approach provides a solid foundation for running Nextcloud reliably in a homelab Kubernetes environment.
