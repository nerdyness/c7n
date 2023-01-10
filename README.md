# c7n
My custodian implementation

## Getting started
* Checkout this repository
  * `git checkout https://github.com/nerdyness/c7n.git`
* Explore your options
  * `make`
* Install CDK and other dependencies
  * `make dependencies`
* Install the CDK Stack in backend/
  * `make deploy`
* Add the CodeCommit repo as a remote to this repository
  * `git remote add codecommit URL`
* Push this code to CodeCommit
  * `git push codecommit`
* Execute the CodeBuild pipeline
  * `make cloud-deploy`
