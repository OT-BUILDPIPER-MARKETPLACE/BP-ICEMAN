VERSION ?= 1.0
CONF_PATH ?=${PWD}/config/resize_aws_k8s_resource.yaml

build:
	docker build -t opstree/iceman:${VERSION} .
run:
	docker run -it --rm --name iceman -v ${CONF_PATH}:/opt/config/resize_aws_k8s_resource.yaml:ro -e SCHEDULE_ACTION=${ACTION} -e CONF_PATH='/opt/config/resize_aws_k8s_resource.yaml' -v ~/.kube:/root/.kube opstree/iceman:${VERSION} 
