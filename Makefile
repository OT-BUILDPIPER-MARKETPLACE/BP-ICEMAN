VERSION ?= 1.0
CONF_PATH ?=${PWD}/config/schedule_aws_resources_sample_config.yml

build:
	docker build -t opstree/schedule_aws_resources:$(VERSION) .
run:
	docker run -it --rm --name schedule_aws_resources host -v ${CONF_PATH}:/etc/ot/schedule_aws_resources.yml:ro -e SCHEDULE_ACTION=${ACTION} -e CONF_PATH='/etc/ot/schedule_aws_resources.yml' -v ~/.aws:/root/.aws opstree/schedule_aws_resources:${VERSION} 
