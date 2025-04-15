## Ceph S3 Test

Pull submodules first

```bash
git submodule update --init --recursive
```

Install `tox`

```bash
uv tool install tox
```

Copy `s3tests.conf.SAMPLE` to `s3tests.conf` and edit it to point to your Ceph cluster.

```bash
cp s3tests.conf.SAMPLE s3tests.conf
```

## Build ozone cluster

### Download from github artifact

Download the `gh` command and login to github

```bash
brew install gh
gh auth login
```

Ozone build the binary for your each push
TO download the ozone binary from the github artifact, specify the workflow run id and the repo

```bash
# TODO: if branch specific, get the latest run id from the branch
REPO=github.com/apache/ozone
RUN_ID=14467654746
COMMIT_SHA=$(gh run view $RUN_ID --repo $REPO --json headSha --jq .headSha)
BRANCH_NAME=$(gh run view $RUN_ID --repo $REPO --json headBranch --jq .headBranch)
SANITIZED_BRANCH_NAME=$(echo $BRANCH_NAME | tr '/' '_')
BUILD_DIR=ozone-build/$SANITIZED_BRANCH_NAME-$COMMIT_SHA
mkdir -p $BUILD_DIR
gh run view $RUN_ID --repo $REPO --json headSha,headBranch,createdAt > $BUILD_DIR/commit-meta.json
gh run download $RUN_ID -n ozone-bin --repo $REPO --dir $BUILD_DIR
tar -xzf $BUILD_DIR/ozone-*.tar.gz -C $BUILD_DIR
rm $BUILD_DIR/ozone-*.tar.gz
```

### Start ozone cluster

```bash
cd $BUILD_DIR/ozone-*-SNAPSHOT/compose/ozone
docker compose up -d
docker compose exec scm bash -c "ozone s3 -D=ozone.security.enabled=true revokesecret -y" || true
docker compose exec scm bash -c "ozone s3 -D=ozone.security.enabled=true getsecret -e"
# export AWS_ACCESS_KEY_ID='hadoop'
# export AWS_SECRET_ACCESS_KEY='88359ea01ae53482e6cdb896c960dd8a57c32ee301fe071d07d0d465590e2074'
```

### Run tests

Set the port in s3tests.conf to 9878

Set the [s3 main].access_key and [s3 main].secret_key in s3tests.conf to the values above
# TODO: use python to find the s3tests.conf.SAMPLE file then replace the access_key and secret_key with the parsed values from the above output

```bash
# You should be at the root of the repo
cd s3-tests
S3TEST_CONF=your.conf tox -- s3tests_boto3/functional
```

