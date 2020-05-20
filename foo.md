# c7n

## c7n Policies

Policies are stored as [Jinja templates](http://jinja.pocoo.org/)
and auto-generated based on a flexible, yet somewhat opinionated
structure.

### Getting started

The easiest way to create a policy is to put it in the [policies folder](policies/) and then add it to the right [environment](environments/).

### Environments

#### AWS vs Custodian Environments
The below mapping between AWS Environments and Custodian Environments is followed:

|AWS Environment|Custodian Environment|
|----:|:----|
|Sand[box]|sandbox|
|Prod|prod|
|Dev|standard|
|Test|standard|
|Integration|standard|

#### Global Environments

In AWS, global services such as IAM or S3 are processed in regions `us-east-1` and `us-west-2`. Policies filtering on these resources are only deployed in these regions and can be defined in the "global" environment file.

#### Regional Environments

All other policies that do not check for "global" but for "regional" resources will be deployed to all regions. You can define these policies in the regional environments structure.

### Generate policies

To generate can run `./create_policies.py` followed by the AWS Environment of your choice, for instance:
```bash
./create_policies.py prod # OR
cd ../; invoke generate --env prod
```

The regional policies will be generated in the [c7n/regional](c7n/regional/) directory. NOTE: The entire "[c7n/](c7n/)" directory will be removed and re-generated during a run of `./create_policies.py`!!

Global policies will be generated in the [c7n/global](c7n/global/) directory.

### Policies are inclusive

The above example will create all policies listed in the global & regional
[common.yml](environments/regional/common.yml) __*AND*__ the
[prod environment](environments/regional/prod.yml), in other words: the
[common.yml](environments/regional/common.yml) policies are always included and additional policies can be added per environment for *standard*, *sandbox* and *prod*.

### Policies are flexible
#### Standard, sandbox and prod?
You're probably wondering "what's the deal with standard, sandbox and prod?" Whenever you see these directories, namely in `actions/`, `filters/` and `inputs/` the default behaviour is to look for a file in the environment you're in, i.e. `prod` or `sandbox`. If no file is found in the specific environment, the policy generator will look in `standard` and take the file from there.

Imagine you wanted the same behaviour for `prod` and `standard` environments, but something different in the `sandbox` environment. You won't have to duplicate your file for `prod` and `standard`, instead you can simply place a file in `sandbox` for the sandbox environment, and another file in `standard` which will be picked up by `prod` and `standard`.

#### Snippets
Common snippets like the below notification policy can be placed in the snippets directory and then referred to by it's filename minus the file ending (".yml"). Let's say the following code snippet is in a file called "*notify_transport.yml*". *NOTE:* Avoid dashes (-) and use underscore (\_) for snippet filenames!
```
transport:
  type: sqs
  queue: https://sqs.eu-west-1.amazonaws.com/887599381655/custodian
  region: eu-west-1
```
You can refer to it via `{{notify_transport}}` from within your *filters*, *actions* or the main policy document.

A good example of this can be seen in the iam-users policy, in particular the [actions file](./actions/standard/iam_user-created.yml).

#### Filters and Actions
A Custodian Policy consists of some meta information, filters and actions. Meta information consists of things like a name, description, resource and so forth; while a filter limits the specified resource based on things like tags, or values of certain keys in the configuration. Actions are executed by Custodian if a resource matching the filters is found.

NOTE: that you can use [snippets](#snippets) in *filters*, *actions* or the main policy document.

Also read [Standard, sandbox and prod](#standard-sandbox-and-prod) to understand how the folder structure works.

#### Inputs
Inputs are a special breed. You will notice that some policies are repetitive and only differ on the resource, name and description. Therefore, this framework allows you to configure multiple inputs that can be replaced within a policy. Take the [following policy](./policies/all-svc-auto-tag-user.yml) for example:
```
policies:
{% for input in inputs %}
- name: {{input.resource}}-auto-tag-user
  resource: {{input.resource}}
  description:  |
    Auto-tag {{input.resource}} instances with creator identifier
  mode:
    type: cloudtrail
    role: arn:aws:iam::{account_id}:role/c7n-LambdaExecutionRole
    events:
      {{input.events|indent(6)}}
  filters:
    - "tag:CreatorName": absent
  actions:
    - type: auto-tag-user
      tag: CreatorName
    {{input.actions}}
{% endfor %}
```
This obviously expects some kind of inputs list or array with a structure in it to defining `resource`, `events` and `account_id`. This structure is read from [the inputs folder](./inputs/standard/all-svc-auto-tag-user.yml) and defines a list of in puts, each giving a `resource`, `events` and `account_id` value.

Also read [Standard, sandbox and prod](#standard-sandbox-and-prod) to understand how the folder structure works.

NOTE: You can *NOT* use [snippets](#snippets) in inputs because inputs are read as a plain yaml structure where as actions and filters are rendered as a template.
