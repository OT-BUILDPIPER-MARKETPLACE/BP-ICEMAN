VERSION ?= 0.5
CONF_PATH ?=${PWD}/config/schedule_resources_sample_config.yml

build:
	docker build -t opstree/schedule_instance:$(VERSION) . --network host
run:
	docker run -it --rm --name schedule_instance --network host -v ${CONF_PATH}:/opt/config/schedule_resources.yml:ro -e SCHEDULE_ACTION=${ACTION} -e CONF_PATH='/opt/config/schedule_resources.yml' -v ~/.aws:/root/.aws opstree/schedule_instance:${VERSION} 
