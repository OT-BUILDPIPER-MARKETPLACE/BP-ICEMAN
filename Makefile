VERSION ?= 1.0
CONF_PATH ?=${PWD}/config/schedule_resources_config.yml

build:
	docker build -t opstree/schedule_resources:$(VERSION) .
run:
	docker run -it --rm --name schedule_resources -v ${CONF_PATH}:/etc/ot/schedule_resources.yml:ro -e K8s_SCHEDULE_ACTION=${K8s_ACTION} -e AWS_SCHEDULE_ACTION=${AWS_ACTION} -e CONF_PATH='/etc/ot/schedule_resources.yml' -v ~/.aws:/root/.aws -v ~/.kube:/root/.kube opstree/schedule_resources:${VERSION} 
