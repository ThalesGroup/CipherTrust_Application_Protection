# Reduce Risk and Accelerate Value: Snowflake Cortex AI and Thales Data Protection

## Cortex AI as a sensitive-data security enabler

Data is now a core business asset, but sensitive data brings a difficult
responsibility. Organizations must make data useful to analysts, developers,
and AI initiatives while reducing exposure, demonstrating compliance, and
retaining control over the encryption keys that protect their most valuable
information.

The Thales and Snowflake partnership helps organizations address this challenge
without turning every data project into a security engineering project.
Snowflake brings data discovery, classification, governance, and the scale of
the AI Data Cloud. Thales brings policy-based data protection, centralized key
management, and customer choice across deployment models. Together, they help
organizations create a practical, defense-in-depth strategy for sensitive data.

There is a simple way to express why this matters: **you cannot have a good
analytics strategy without a good data strategy, and you cannot have a good data
strategy without a good security strategy.** The Thales and Snowflake
partnership helps bring those strategies together, so organizations can use data
with greater confidence instead of treating security as an afterthought.

![Workflow from Cortex-assisted discovery through column tags, Snowpark Container Services, Thales CRDP, and CipherTrust policy and key management.](assets/cortex-thales-protection-workflow.png)

*Figure 1. Snowflake governance and Thales protection work together to support a
repeatable lifecycle for sensitive data.*

## Reduce risk without slowing down the business

Organizations increasingly need to use sensitive data in analytics, reporting,
and AI workloads. The risk is not limited to storing the data: exposure can also
occur when data is copied, shared, queried, or made available to the wrong user.
Protection needs to follow the data and be enforced consistently.

Thales CipherTrust REST Data Protection (CRDP) provides policy-based options
such as encryption, tokenization, masking, and controlled reveal. Instead of
embedding cryptographic decisions in every application or pipeline, teams call a
central service while security administrators manage the policies, keys, and
authorized access rules. This separation of duties can reduce the chance that
security controls drift as data products evolve.

For Snowflake customers, the result is a stronger defense-in-depth posture.
Snowflake’s platform controls continue to protect the environment, while Thales
adds data-centric protection and independent policy control around sensitive
fields. If a user, application, or dataset is accessed outside its intended
context, protected values help limit the exposure of usable cleartext.

## Improve compliance with a visible, repeatable control model

Compliance is difficult when organizations cannot show where sensitive data is
located, how it was protected, and who can access it. Snowflake’s built-in
sensitive-data classification can identify sensitive data at column level and
apply semantic and privacy tags. That creates a governance signal that can be
used to drive consistent action rather than relying on manually maintained lists
of tables and fields.

With Cortex-assisted workflows, security teams can describe a goal in plain
language, such as identifying PII in a database and applying a protection tag.
The workflow can still include human review and dry-run approval before data is
changed. This makes it easier for administrators to move from discovery to
action while keeping change control intact.

Once a column is tagged, the tag can trigger a consistent Thales protection
workflow. Organizations can then use governed Snowflake views or the Thales JDBC
Driver to make protected data usable for the right people. A masked user sees
protected values; an authorized user sees cleartext only when role and policy
permit it. The policy decision is centralized instead of reproduced in every
report and application.

![Masked user sees protected tokens while an authorized user receives governed cleartext through a reveal view or JDBC Driver.](assets/governed-data-access.png)

*Figure 2. Sensitive data can remain useful while access to cleartext is governed
by role and centrally managed policy.*

## Support data sovereignty and customer key control

For many organizations, data sovereignty is not simply about the region where
data resides. It is also about who controls the keys and policies that govern
access to sensitive information. Thales enables customers to retain control of
encryption keys and data-protection policies, helping them meet internal
requirements and demonstrate appropriate controls to auditors and regulators.

Customer choice is important because regulatory, operational, and risk
requirements differ. Thales supports physical, virtual, cloud, hybrid-cloud,
and multi-cloud deployment options. Where required, organizations can use
FIPS-certified Thales hardware security modules and related key-management
infrastructure as part of their broader cryptographic control strategy. This
allows the security model to align with an organization’s policies without
forcing a one-size-fits-all approach.

## Shorten the path from discovery to protection

The time between discovering a risk and applying a control matters. Separate
tools for discovery, classification, ticketing, integration, and policy
enforcement can increase operational complexity and slow down delivery.

Snowflake reduces that complexity by bringing classification and governance
close to the data. Cortex can make the operational experience more approachable
for security teams by helping turn natural-language objectives into reviewable
Snowflake work. Thales provides the protection engine and centralized policy
layer. Snowpark Container Services gives organizations a deployment model that
can run the integration alongside their Snowflake workloads.

Running the protection service in Snowpark Container Services can simplify
deployment and lifecycle management by keeping the service within the Snowflake
environment. It can also reduce unnecessary network hops compared with a design
that routes every protection request through an external integration point. The
actual performance outcome depends on workload shape, regional placement,
policy, and service sizing, but bulk REST protection and local service-to-service
communication create a strong foundation for efficient operation.

## A practical choice for modern data programs

The Thales and Snowflake combination is about more than encryption. It gives
organizations a way to discover sensitive data, apply the right protections,
govern cleartext access, and retain control over keys and policy as their data
estate grows.

That translates into business value: lower exposure risk, clearer evidence for
compliance, stronger sovereignty controls, and a faster route from data
discovery to protection. Most importantly, it helps security and data teams
work together without making secure data use the bottleneck to innovation. In
that sense, Cortex AI is not only a productivity tool: paired with Thales, it can
be a practical sensitive-data security enabler for a modern data strategy.

## Further reading

- [Thales: Data Protection for Snowflake AI Data Cloud](https://cpl.thalesgroup.com/resources/encryption/snowflake-ai-data-cloud-data-protection-solution-brief)
- [Thales: CipherTrust RESTful Data Protection](https://cpl.thalesgroup.com/encryption/ciphertrust-restful-data-protection)
- [Snowflake: Introduction to sensitive-data classification](https://docs.snowflake.com/en/user-guide/classify-intro)
- [Snowflake: Snowpark Container Services](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/working-with-services)
