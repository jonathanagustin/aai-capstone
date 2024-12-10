# rollback_manager.py
"""
rollback_manager.py

Implements a RollbackManager that checks system health metrics (error rate, latency, fairness)
and triggers a Kubernetes rollback if conditions degrade. Ensures stable production environments
and preserves trust.

Key concepts:
- Automated rollbacks on metric degradation
- Integration with Kubernetes APIs
- Rapid response to protect user experience
"""

import kubernetes as k8s
import logging

class RollbackConfig:
    def __init__(self,error_threshold,latency_threshold,fairness_threshold):
        """
        error_threshold: maximum allowed error rate before rollback
        latency_threshold: maximum allowed p95 latency
        fairness_threshold: minimum fairness score required
        """
        self.error_threshold=error_threshold
        self.latency_threshold=latency_threshold
        self.fairness_threshold=fairness_threshold

class RollbackManager:
    def __init__(self, config: RollbackConfig, namespace='default'):
        self.config = config
        self.k8s_client = k8s.client.AppsV1Api()
        self.namespace = namespace

    def check_health(self, metrics):
        """
        Check if current metrics exceed defined thresholds.
        metrics: {'error_rate':float, 'p95_latency':float, 'fairness_score':float}
        """
        if metrics['error_rate']>self.config.error_threshold:
            return False,'High error rate'
        if metrics['p95_latency']>self.config.latency_threshold:
            return False,'High latency'
        if metrics['fairness_score']<self.config.fairness_threshold:
            return False,'Fairness violation'
        return True,None

    def initiate_rollback(self, deployment_name: str, reason: str):
        """
        Initiate a Kubernetes rollback to the last known good revision if available.
        """
        try:
            deployment=self.k8s_client.read_namespaced_deployment(deployment_name,self.namespace)
            revisions=self.k8s_client.list_namespaced_replica_set(
                self.namespace,label_selector=f"app={deployment_name}")
            last_good=self._find_last_good_revision(revisions.items)
            if not last_good:
                logging.error("No good revision found for rollback")
                return False
            body={
              "kind": "DeploymentRollback",
              "apiVersion": "apps/v1",
              "name": deployment_name,
              "rollbackTo": {"revision":last_good.metadata.annotations['revision']}
            }
            self.k8s_client.create_namespaced_deployment_rollback(
                deployment_name,self.namespace,body)
            logging.info(f"Rollback initiated for {deployment_name}: {reason}")
            return True
        except k8s.client.rest.ApiException as e:
            logging.error(f"Rollback failed: {str(e)}")
            return False

    def _find_last_good_revision(self,rs_list):
        # Placeholder logic: just take the last ReplicaSet as last good revision
        return rs_list[-1] if rs_list else None
