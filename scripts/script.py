from kubernetes import client, config
import sys
import os
import argparse
import logging
import yaml
import json
import json_log_formatter
from botocore.exceptions import ClientError
from otfilesystemlibs import yaml_manager

SCHEDULE_ACTION_ENV_KEY = "SCHEDULE_ACTION"
CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/var/log/ot/aws-resource-scheduler.log"

FORMATTER = json_log_formatter.VerboseJSONFormatter()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

FILE_HANDLER = logging.FileHandler(LOG_PATH)
STREAM_HANDLER = logging.StreamHandler(sys.stdout)

FILE_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)


def deployment_having_annotation(cli, namespace):
    deployments = []
    for x in range(len(cli.list_namespaced_deployment(namespace=namespace).items)):
        try:
            if cli.list_namespaced_deployment(namespace=namespace).items[x].metadata.annotations['start_stop_schedule']:
                deployments.append(cli.list_namespaced_deployment(
                    namespace=namespace).items[x].metadata.name)
        except:
            pass
    return deployments


def statefulset_having_annotation(cli, namespace):
    statefulset = []
    for x in range(len(cli.list_namespaced_stateful_set(namespace=namespace).items)):
        try:
            if cli.list_namespaced_stateful_set(namespace=namespace).items[x].metadata.annotations['start_stop_schedule']:
                statefulset.append(cli.list_namespaced_stateful_set(
                    namespace=namespace).items[x].metadata.name)
        except:
            pass
    return statefulset


def deployment_replica_change(cli, properties, deployments):
    namespace = properties['namespace']
    conf_path = properties['folder_structure']
    replicas = properties['replicas']

    for deployment in deployments:
        body = {"apiVersion": "apps/v1", "kind": "Deployment",
                "spec": {"replicas": replicas, }}
        print(cli.patch_namespaced_deployment_scale(
            namespace=namespace, name=deployment, body=body))


def statefulset_replica_change(cli, properties, statefulset):
    namespace = properties['namespace']
    conf_path = properties['folder_structure']
    replicas = properties['replicas']
    for statefulset in statefulset:
        body = {"apiVersion": "apps/v1", "kind": "Deployment",
                "spec": {"replicas": replicas, }}
        print(cli.patch_namespaced_stateful_set_scale(
            namespace=namespace, name=statefulset, body=body))


def _resourceManagerFactory(properties, kube_context, args):

    instance_ids = []

    try:

        LOGGER.info(f'Connecting to Kubernetes Cluster.')

        if kube_context:
            config.load_kube_config(context=kube_context)
        else:
            config.load_kube_config(context=kube_context)

        LOGGER.info(f'Connection to EKS Cluster established.')

        config_namespace = properties['namespace']
        for property in properties['folder_structure']:
            # print(property)
            for resource in property:

                if resource == "k8s":

                    if properties['deployment_annotations']:

                        LOGGER.info(f'Reading deployment annotations')

                        for schedule in properties['deployment_annotations']:
                            if schedule:
                                deployment_annot = properties['deployment_annotations']
                            else:
                                deployment_annot = "false"

                        if deployment_annot:

                            LOGGER.info(
                                f'Found deployment annotations details for filtering : {deployment_annot}')

                            v2client = client.AppsV1Api()

                            LOGGER.info(
                                f'Scanning deployments based on annotations {deployment_annot} provided')

                            deployments = deployment_having_annotation(
                                v2client, config_namespace)

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

                    if properties['sts_annotations']:

                        LOGGER.info(f'Reading statefulset annotations')

                        for schedule in properties['sts_annotations']:
                            if schedule:
                                sts_annot = properties['sts_annotations']
                            else:
                                sts_annot = "false"

                        if sts_annot:

                            LOGGER.info(
                                f'Found statefulset annotations details for filtering : {sts_annot}')

                            v2client = client.AppsV1Api()

                            LOGGER.info(
                                f'Scanning deployments based on annotations {deployment_annot} provided')

                            statefulset = statefulset_having_annotation(
                                v2client, config_namespace)

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

                else:
                    LOGGER.info("Scanning K8s service details in config")

    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception(' Authentication Failure!!!! .. Please mention valid profile in property file or use valid credentials').with_traceback(
                e.__traceback__)
        else:
            raise e
    except KeyError as e:
        raise Exception(f'Failed fetching env {SCHEDULE_ACTION_ENV_KEY} value. Please add this env variable').with_traceback(
            e.__traceback__)


def _resizeResources(args):

    LOGGER.info(
        f'Fetching properties from conf file: {args.property_file_path}.')

    yaml_loader = yaml_manager.getYamlLoader()
    properties = yaml_loader._loadYaml(args.property_file_path)

    LOGGER.info(f'Properties fetched from conf file.')

    if properties:
        if "context" in properties:
            context = properties['context']
        else:
            context = None

        _resourceManagerFactory(properties, context, args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file",
                        default=os.environ[CONF_PATH_ENV_KEY], type=str)
    args = parser.parse_args()
    _resizeResources(args)
