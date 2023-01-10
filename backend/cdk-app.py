from constructs import Construct
from aws_cdk import App, Stack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_iam as iam

class ECR(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)

        bucket = s3.Bucket(
            self, "c7n-output-bucket",
            # FIXME, determine account ID automagically
            bucket_name="c7n-output-bucket-888588296919"
        )

        # Add a Lambda that calls c7n once per day via a CodeBuild run.
        cc = codecommit.Repository(self, "c7n-code-repo",
                repository_name="c7n-code-repo")

        c7n_run = codebuild.Project(
            self, "c7n-run-codebuild",
            source=codebuild.Source.code_commit(repository=cc),
            build_spec=codebuild.BuildSpec.from_source_filename(filename="buildspec.c7n-run.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_docker_registry("cloudcustodian/c7n")
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
                build_image=codebuild.LinuxBuildImage.from_docker_registry("cloudcustodian/c7n-org")
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


app = App()
ECR(app, "CloudCustodian")
app.synth()
