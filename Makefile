build:
	docker build -t opstree/schedule_instance:$(VERSION) .
run:
	docker run -it --rm --name schedule_instance -v ${CONF_PATH}:/opt/config/schedule_resources_backup.yml:ro -e SCHEDULE_ACTION=${ACTION} -e CONF_PATH='/opt/config/schedule_resources_backup.yml' -v ~/.aws:/root/.aws opstree/schedule_instance:${VERSION}

run-debug:
	docker run -it --rm --name schedule_instance -v ${CONF_PATH}:/opt/config/schedule_resources_backup.yml:ro -e SCHEDULE_ACTION=${ACTION} -e CONF_PATH='/opt/config/schedule_resources_backup.yml' -v ~/.aws:/root/.aws --entrypoint bash opstree/schedule_instance:${VERSION} 
