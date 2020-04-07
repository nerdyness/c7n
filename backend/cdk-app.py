from aws_cdk import (
    core,
    aws_ecr as ecr,
    # aws_ec2 as ec2,
    aws_s3 as s3,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_iam as iam
)


class ECR(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)

        bucket = s3.Bucket(
            self, "c7n-output-bucket",
            bucket_name="c7n-output-bucket-asdfasdf"
        )

        # Add a Lambda that calls c7n once per day via a CodeBuild run.

        # This is only needed because of an incompatible upstream image (see
        # https://github.com/cloud-custodian/cloud-custodian/issues/5560)
        my_ecr = ecr.Repository(self, "my-c7n-repo",
                repository_name="c7n-registry")

        cc = codecommit.Repository(self, "c7n-code-repo",
                repository_name="c7n-code-repo")

        c7n_run = codebuild.Project(
            self, "c7n-run-codebuild",
            source=codebuild.Source.code_commit(repository=cc),
            build_spec=codebuild.BuildSpec.from_source_filename(filename="buildspec.c7n-run.yml"),
            environment=codebuild.BuildEnvironment(
                # See above
                # build_image=codebuild.LinuxBuildImage.from_docker_registry("cloudcustodian/c7n")
                build_image=codebuild.LinuxBuildImage.from_ecr_repository(my_ecr)
            ),
            project_name="c7n-run",
            artifacts=codebuild.Artifacts.s3(
                    bucket=bucket,
                    encryption=False,
                    identifier="c7n-run-output",
                    include_build_id=True,
                    name="c7n-run-output",
                    package_zip=False,
                    path="c7n/",
            ),
        )

        c7n_org = codebuild.Project(
            self, "c7n-org-codebuild",
            source=codebuild.Source.code_commit(repository=cc),
            build_spec=codebuild.BuildSpec.from_source_filename(filename="./buildspec.c7n-org.yml"),
            environment=codebuild.BuildEnvironment(
                # build_image=codebuild.LinuxBuildImage.from_docker_registry("cloudcustodian/c7n-org")
                build_image=codebuild.LinuxBuildImage.from_ecr_repository(my_ecr, tag="org")
            ),
            project_name="c7n-org",
            artifacts=codebuild.Artifacts.s3(
                    bucket=bucket,
                    encryption=False,
                    identifier="c7n-org-output",
                    include_build_id=True,
                    name="c7n-org-output",
                    package_zip=False,
                    path="c7n-org/",
            ),
        )

        # Add premissions for c7n-run and c7n-org roles
        c7n_run_policy = iam.PolicyStatement(
            actions=[
                # FIXME!!!!
                "*",
            ],
            resources=["*"],
        )
        c7n_run.add_to_role_policy(c7n_run_policy)

        c7n_org_policy = iam.PolicyStatement(
            actions=[
                "sts:AssumeRole",
            ],
            resources=["arn:aws:iam::*:role/c7n-deploy"],
        )
        c7n_org.add_to_role_policy(c7n_org_policy)


app = core.App()
ECR(app, "CloudCustodian")
app.synth()
