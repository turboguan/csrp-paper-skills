# Freeze policy

Once this freeze PR is merged, files under this directory are treated as immutable v1.0 protocol artifacts.

## Allowed after freeze

- filling separate reviewer output files created from the frozen templates;
- creating adjudicated Gold output as a new file;
- adding machine-generated results that reference this freeze version;
- creating a new versioned freeze directory.

## Not allowed

- changing candidate claim text in place;
- changing pair membership;
- changing relation definitions;
- changing the statistical primary endpoint;
- changing the primary architecture contrast;
- back-editing reviewer raw sheets;
- replacing source identifiers without creating a new version.

## Corrections

Any substantive correction requires:
1. new version directory;
2. changelog;
3. reason for revision;
4. updated freeze manifest;
5. clear statement whether prior benchmark results are invalidated.
