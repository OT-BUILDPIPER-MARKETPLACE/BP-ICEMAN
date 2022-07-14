import os, logging
import schedule_resource_logger
from kubernetes import client, config
from botocore.exceptions import ClientError

import k8s_kube_session ,k8s_deployment_factory, k8s_sts_factory

SCHEDULE_ACTION_ENV_KEY = "K8s_SCHEDULE_ACTION"
LOG_PATH = "/var/log/ot/aws-resource-scheduler.log"

LOGGER = schedule_resource_logger._get_logging(LOG_PATH)

def _schedule_deployment(properties, namespace , args):

    if properties['k8s']['deployment_annotations']:

            LOGGER.info(f'Reading deployment annotations')

            for schedule in properties['k8s']['deployment_annotations']:
                if schedule:
                    deployment_annot = properties['k8s']['deployment_annotations']
                else:
                    deployment_annot = "false"

            if deployment_annot:

                LOGGER.info(
                    f'Found deployment annotations details for filtering : {deployment_annot}')

                v2client = client.AppsV1Api()
                k8sDeploymentActions = k8s_deployment_factory.k8sDeploymentActions(v2client)

                LOGGER.info(
                    f'Scanning deployments based on annotations {deployment_annot} provided')

                deployments = k8sDeploymentActions._get_deployments_with_annotation(
                     namespace, deployment_annot)

                if deployments:

                    LOGGER.info(
                        f'Found deployments resources {deployments}  based on annotations provided: {deployment_annot} in the namesapce : {namespace}')

                    if os.environ[SCHEDULE_ACTION_ENV_KEY] == "start":

                        print(k8sDeploymentActions.deployments_replica_change(
                             properties, deployments, namespace, "start"))

                    if os.environ[SCHEDULE_ACTION_ENV_KEY] == "stop":

                        print(k8sDeploymentActions.deployments_replica_change(
                             properties, deployments, namespace, "stop"))
                    else:
                        logging.error(
                            f"{SCHEDULE_ACTION_ENV_KEY} env not set or value is invalid. Valid value: start, stop")

                else:
                    LOGGER.warning(
                        f'No deployments found on the basis of tag filters provided in conf file in context {properties["k8s"]["context"]} in the namespace: {namespace}')
            else:
                LOGGER.warning(f' No deployment annotations details mentioned for filtering in the config file')

def _schedule_sts(properties, namespace , args):

    if properties['k8s']['sts_annotations']:

        LOGGER.info(f'Reading statefulset annotations')

        for schedule in properties['k8s']['sts_annotations']:
            if schedule:
                sts_annot = properties['k8s']['sts_annotations']
            else:
                sts_annot = "false"

        if sts_annot:

            LOGGER.info(
                f'Found statefulset annotations details for filtering : {sts_annot}')

            v2client = client.AppsV1Api()
            k8sStsActions = k8s_sts_factory.k8sStsActions(v2client)


            LOGGER.info(
                f'Scanning statefulset based on annotations {sts_annot} provided')

            statefulset = k8sStsActions._get_statefulsets_with_annotation(
                 namespace, sts_annot)

            if statefulset:

                LOGGER.info(
                    f'Found statefulset resources {statefulset}  based on annotations provided: {sts_annot} in the namespace {namespace}')

                if os.environ[SCHEDULE_ACTION_ENV_KEY] == "start":

                    print(k8sStsActions.statefulsets_replica_change(
                         properties, statefulset, namespace, "start"))

                if os.environ[SCHEDULE_ACTION_ENV_KEY] == "stop":

                    print(k8sStsActions.statefulsets_replica_change(
                         properties, statefulset, namespace, "stop"))

                else:
                    logging.error(
                        f"{SCHEDULE_ACTION_ENV_KEY} env not set or value is invalid. Valid value: start, stop")

            else:
                LOGGER.warning(
                    f'No statefulset found on the basis of tag filters provided in conf file in context {properties["k8s"]["context"]} in the namespace: {namespace} ')

    else:
        LOGGER.warning(
            f'Found annotations in config file but no statefulset annotations details mentioned for filtering')


def _resourceManagerFactory(properties, kube_context, resource_type,  args):

    try:

        LOGGER.info(f'Connecting to Kubernetes Cluster.')

        config.load_kube_config(context=kube_context)

        LOGGER.info(f'Connection to EKS Cluster established.')

        namespaces = properties['k8s']['namespaces']

        for namespace in namespaces:

            if resource_type == "deployment":
                _schedule_deployment(properties, namespace , args)
            elif resource_type == "sts":
                _schedule_sts(properties, namespace , args)
            else:
                LOGGER.info(f'Invalid Resource type provided. Valid values: [deployment,sts]')


    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception(' Authentication Failure!!!! .. Please mention valid profile in property file or use valid credentials').with_traceback(
                e.__traceback__)
        else:
            raise e
    except KeyError as e:
        raise Exception(f'Failed fetching env {SCHEDULE_ACTION_ENV_KEY} value. Please add this env variable').with_traceback(
            e.__traceback__)


