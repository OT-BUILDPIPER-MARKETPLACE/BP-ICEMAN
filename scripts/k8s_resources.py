import os
import schedule_resource_logger
from kubernetes import client, config
from botocore.exceptions import ClientError


SCHEDULE_ACTION_ENV_KEY = "K8s_SCHEDULE_ACTION"
LOG_PATH = "/ot/aws-resource-scheduler.log"


LOGGER = schedule_resource_logger._get_logging(LOG_PATH)


def deployment_having_annotation(cli, namespace, deployment_annot):
    deployments = []
    annotation = list(deployment_annot)
    for x in range(len(cli.list_namespaced_deployment(namespace=namespace).items)):
        try:
            if cli.list_namespaced_deployment(namespace=namespace).items[x].metadata.annotations[annotation[0]] == "true" :
                deployments.append(cli.list_namespaced_deployment(
                    namespace=namespace).items[x].metadata.name)
        except:
            pass
    return deployments


def statefulset_having_annotation(cli, namespace, sts_annot):
    statefulset = []
    annotation = list(sts_annot)
    for x in range(len(cli.list_namespaced_stateful_set(namespace=namespace).items)):
        try:
            if cli.list_namespaced_stateful_set(namespace=namespace).items[x].metadata.annotations[annotation[0]] == "true" :
                statefulset.append(cli.list_namespaced_stateful_set(
                    namespace=namespace).items[x].metadata.name)
        except:
            pass
    return statefulset


def deployment_replica_change(cli, properties, deployments):
    namespace = properties['k8s']['namespace']
    replicas = properties['k8s']['replicas']

    for deployment in deployments:
        body = {"apiVersion": "apps/v1", "kind": "Deployment",
                "spec": {"replicas": replicas, }}
        print(cli.patch_namespaced_deployment_scale(
            namespace=namespace, name=deployment, body=body))


def statefulset_replica_change(cli, properties, statefulset):
    namespace = properties['k8s']['namespace']
    replicas = properties['k8s']['replicas']
    for statefulset in statefulset:
        body = {"apiVersion": "apps/v1", "kind": "Deployment",
                "spec": {"replicas": replicas, }}
        print(cli.patch_namespaced_stateful_set_scale(
            namespace=namespace, name=statefulset, body=body))


def _resourceManagerFactory(properties, kube_context, resource_type,  args):

    try:

        LOGGER.info(f'Connecting to Kubernetes Cluster.')

        config.load_kube_config(context=kube_context)

        LOGGER.info(f'Connection to EKS Cluster established.')

        namespace = properties['k8s']['namespace']

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

                LOGGER.info(
                    f'Scanning deployments based on annotations {deployment_annot} provided')

                deployments = deployment_having_annotation(
                    v2client, namespace, deployment_annot)

                if deployments:

                    LOGGER.info(
                        f'Found deployments resources {deployments}  based on annotations provided: {deployment_annot}')

                    if os.environ[SCHEDULE_ACTION_ENV_KEY] == "resize":

                        deployment_replica_change(
                            v2client, properties, deployments)
                    else:
                        logging.error(
                            f"{SCHEDULE_ACTION_ENV_KEY} env not set")

                else:
                    LOGGER.warning(
                        f'No deployments found on the basis of tag filters provided in conf file in context {properties["context"]} ')
            else:
                LOGGER.warning(f' No deployment annotations details mentioned for filtering in the config file')
                
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

                LOGGER.info(
                    f'Scanning deployments based on annotations {deployment_annot} provided')

                statefulset = statefulset_having_annotation(
                    v2client, namespace, sts_annot)

                if statefulset:

                    LOGGER.info(
                        f'Found statefulset resources {statefulset}  based on annotations provided: {sts_annot}')

                    if os.environ[SCHEDULE_ACTION_ENV_KEY] == "resize":

                        statefulset_replica_change(
                            v2client, properties, statefulset)
                    else:
                        logging.error(
                            f"{SCHEDULE_ACTION_ENV_KEY} env not set")

                else:
                    LOGGER.warning(
                        f'No statefulset found on the basis of tag filters provided in conf file in context {properties["context"]} ')

        else:
            LOGGER.warning(
                f'Found annotations in config file but no statefulset annotations details mentioned for filtering')


    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception(' Authentication Failure!!!! .. Please mention valid profile in property file or use valid credentials').with_traceback(
                e.__traceback__)
        else:
            raise e
    except KeyError as e:
        raise Exception(f'Failed fetching env {SCHEDULE_ACTION_ENV_KEY} value. Please add this env variable').with_traceback(
            e.__traceback__)

