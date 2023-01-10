C7N_RUN_CODEBUILD_PROJECT=c7n-run
C7N_ORG_CODEBUILD_PROJECT=c7n-org
CDK_ROOT=backend
SHELL=/bin/bash
DOCKER_MAPPING=docker run --rm -it \
  -v $$(pwd)/custodian/output:/home/custodian/output \
  -v $$(pwd)/custodian/policies:/home/custodian/policies \
  -v $$(pwd)/custodian/c7n-org:/home/custodian/c7n-org \
  -v $(HOME)/.aws/:/home/custodian/.aws/:ro \
  --env-file <(env | grep "^AWS") \
  --entrypoint /bin/bash \
  cloudcustodian/c7n-org

.PHONY: help
help: ## Display this help text
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: bootstrap
bootstrap: ## Install the CDK Toolkit (needed for the CDK)
	cd $(CDK_ROOT); pipenv run cdk bootstrap

.PHONY: dependencies
dependencies: ## Install the Python dependencies
	# npm install -g aws-cdk
	cd $(CDK_ROOT); pipenv install

.PHONY: pip-update
pip-update: ## Update your Python dependencies
	cd $(CDK_ROOT); pipenv update

.PHONY: synth
synth: ## Print out the CloudFormation code for this app
	cd $(CDK_ROOT); pipenv run cdk synth

.PHONY: deploy
deploy: ## Deploy the CDK Stack
	cd $(CDK_ROOT); pipenv run cdk deploy

.PHONY: diff
diff: ## Show the differences between what is local and what is deployed
	cd $(CDK_ROOT); pipenv run cdk diff || true  # Exits non-zero if there is a diff.

.PHONY: docs
docs: ## Attempt to open the CDK documentation in a browser
	cd $(CDK_ROOT); pipenv run cdk docs

.PHONY: destroy
destroy: ## Destroy the CDK Stack
	cd $(CDK_ROOT); pipenv run cdk destroy

.PHONY: show
show: ## Show the CDK App & Stacks
	cd $(CDK_ROOT); pipenv run cdk ls

.PHONY: cloud-run
cloud-run: ## Do a custodian run in AWS CodeBuild
	aws codebuild start-build --project-name $(C7N_RUN_CODEBUILD_PROJECT)

.PHONY: cloud-deploy
cloud-deploy: ## Do a c7n-org run in AWS CodeBuild
	aws codebuild start-build --project-name $(C7N_ORG_CODEBUILD_PROJECT)

.PHONY: docker-run
docker-run: ## Do a custodian run in the c7n Docker Image (w/o cache)
	$(DOCKER_MAPPING) \
	  -c "custodian run \
	    --output-dir ./output/ \
	    ./policies/*.yml"


.PHONY: docker-shell
docker-shell: ## Drop into a shell in the c7n Docker Image
	$(DOCKER_MAPPING)

# Un-comment this if you don't want the commands echo'd before they run.
.SILENT:
