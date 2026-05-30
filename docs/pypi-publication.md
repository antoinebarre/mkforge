# PyPI Publication

This project publishes `mkforge` to PyPI from Git tags only.

## Package Release

1. Update the package version in `pyproject.toml`.
2. Run the full local quality gate:

   ```bash
   make ci
   ```

3. Validate the distributions locally:

   ```bash
   make check-dist
   ```

4. Commit the version change.
5. Create and push a matching tag:

   ```bash
   git tag v0.1.0
   git push origin main
   git push origin v0.1.0
   ```

The tag must match the package version exactly. For example, version `0.1.0`
must be published from tag `v0.1.0`.

## GitHub Publication

GitHub publishes with PyPI Trusted Publishing.

1. In PyPI, open the `mkforge` project publishing settings.
2. Add a trusted publisher for GitHub Actions.
3. Use these values:

   ```text
   Owner: antoinebarre
   Repository name: mkforge
   Workflow name: publish.yml
   Environment name: pypi
   ```

4. In GitHub, create an environment named `pypi`.
5. Push a tag named `v<version>`.

The GitHub workflow checks the tag, runs `make ci`, builds distributions in
`work/dist`, verifies them with Twine, then publishes to PyPI.

## GitLab Publication

GitLab publishes with a PyPI API token stored as a protected CI/CD variable.

1. Create a PyPI API token scoped to the `mkforge` project.
2. In GitLab, add protected masked CI/CD variables:

   ```text
   TWINE_USERNAME=__token__
   TWINE_PASSWORD=<pypi-token>
   ```

3. Protect release tags that match `v*`.
4. Push a tag named `v<version>`.

The GitLab pipeline checks the tag, runs `make ci`, builds distributions in
`work/dist`, verifies them with Twine, then uploads to PyPI.

