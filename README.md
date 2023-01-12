# c7n
My dummy custodian implementation, currently hard-coded to eu-north-1 region.

## Getting started
* Checkout this repository
  * `git checkout https://github.com/nerdyness/c7n.git`
* Explore your options
  * `make`
* Install CDK and other dependencies
  * `make dependencies`
* Install the CDK Stack in [backend/](backend/) and bootstrap the CDK in your account
  * `make deploy bootstrap`
* Add the CodeCommit repo as a remote to this repository
  * `git remote add codecommit codecommit::eu-north-1://c7n-code-repo`
* Push this code to CodeCommit
  * `git push codecommit`
* Execute the CodeBuild pipeline. This will run c7n-org to deploy the custodian policies in the [c7n-org accounts](custodian/c7n-org/config.yml)
  * `make cloud-deploy`
