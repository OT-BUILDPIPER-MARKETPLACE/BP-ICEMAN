build:
	docker build -t opstree/schedule_instance:0.4 . --network host

run-start:
	docker run -it --rm --name schedule_instance -v ${PWD}/config/schedule_resources.yml:/opt/config/schedule_resources.yml:ro -e SCHEDULE_ACTION='start' -e CONF_PATH='/opt/config/schedule_resources.yml' -v ~/.aws:/root/.aws opstree/schedule_instance:0.4

run-debug-start:
	docker run -it --rm --name schedule_instance -v ${PWD}/config/schedule_resources.yml:/opt/config/schedule_resources.yml:ro -e SCHEDULE_ACTION='start' -e CONF_PATH='/opt/config/schedule_resources.yml' -v ~/.aws:/root/.aws --entrypoint bash opstree/schedule_instance:0.4

run-stop:
	docker run -it --rm --name schedule_instance -v ${PWD}/config/schedule_resources.yml:/opt/config/schedule_resources.yml:ro -e SCHEDULE_ACTION='stop' -e CONF_PATH='/opt/config/schedule_resources.yml' -v ~/.aws:/root/.aws opstree/schedule_instance:0.4

run-debug-stop:
	docker run -it --rm --name schedule_instance -v ${PWD}/config/schedule_resources.yml:/opt/config/schedule_resources.yml:ro -e SCHEDULE_ACTION='stop' -e CONF_PATH='/opt/config/schedule_resources.yml' -v ~/.aws:/root/.aws --entrypoint bash opstree/schedule_instance:0.4

