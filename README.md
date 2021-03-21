# daman

## description

`daman` aims at providing a relatively simple solution to the challenge of sharing data between various multiple individuals/machines in the context of a python-development workflow. This solution relies on cloud storage and allows to control the amount of local disc space used for data management.

## setup & configure

### Install

This package is available through **pip** and can directly be installed as follows by running `pip install daman`.

### cloud provider

#### AWS: S3 Bucket

Should your AWS account not yet configured on your current machine, retrieve the following information:
* access_key_id
* secret_access_key

##### using `dm_aws`
you can then simply running the following command:

```shell
dm_aws --access_key_id <access_key_id> --secret_access_key <secret_access_key>
```

##### manually

Alternatively you can create a file at `~/.aws/credentials` and type in the following :
```ini
[default]
aws_access_key_id = <access_key_id>
aws_secret_access_key = <secret_access_key>
```

### configure daman

To finalise the setup phase, it is required to run to provide the following information:

* `storage_name`: Name of the bucket to be used
* `service`: Type of cloud storage used (Currently only `aws` is available).
* `local_dir` **[Optional]**: local directory to store data in. _default is `~/.daman/data/`_
* `allocated_space` **[Optional]**: Disc space to allocate to local directory. By default no limit is set.


```shell
dm_configure --storage_name <storage_name>
--service <service>
```

## how to

### upload

Currently it is only possible to push python object to `daman` data manager.

#### python: `push`

```python
dm.push(
    obj,
    key=key,
    meta=None,
    local=True,
    force=False,
    persist=False)
```


##### Input

* `obj`: `object` - Any pickle serialisable object.
* `key`: `str` - name under which to store the object. will be used to retrieve the object.
* `meta` **[OPTIONAL]**: `object` - Any pickle serialisable meta information to store with the object.
* `local` **[OPTIONAL]**: `bool` - If set to `True` also adds the uploaded data to your local registery.
* `force` **[OPTIONAL]**: `bool` - If `key` is already in use, `force` must be set to `True` in order to force the overwriting of the already stored object.
* `persist` **[OPTIONAL]**: `bool` - If set to `True` ensures the file will not be deleted unless manually requested.

##### Output - `None`

### download

#### python: `pull`

```python
obj, meta = dm.push(
    key=key,
    force=False,
    persist=False)
```

##### Input

* `key`: `str` - key under which the data is stored.
* `force` **[OPTIONAL]**: `bool` - when set to `True` downloads the dataset from cloud service ignoring local version.
* `persist` **[OPTIONAL]**: `bool` - If set to `True` ensures the file will not be deleted unless manually requested.
* `memory_only` **[OPTIONAL]**: `bool` - is set to `True` only loads the data into memory and does not keep a local version unless already available.

##### Output

* `obj`: `object` stored object.
* `meta`: `object` store meta data.

#### terminal: `dm_pull`

```bash
dm_pull --help

usage: dm_pull [-h] --key {} [--force] [--persist]

Sets up daman package.

optional arguments:
  -h, --help  show this help message and exit
  --key {}    key of the file to delete
  --force     When provided forces the download even when the file is already
              available.
  --persist   When provided ensures that the downloaded file is always kept on
              disc on manually deleted.
```

### delete

#### python: `delete`

```python
obj, meta = dm.delete(
    key=key,
    local=True,
    remote=False)
```

##### Input

* `key`: `str` - key under which the data to delete is stored.
* `local` **[OPTIONAL]**: `bool` - if set to `True` will delete local file.
* `remote` **[OPTIONAL]**: `bool` - if set to `True` will delete remote version of the requested key.

##### Output - `None`

#### terminal: `dm_delete`

```shell
dm_delete --help

Sets up daman package.
optional arguments:
  -h, --help  show this help message and exit
  --key {}    key of the file to delete
  --remote    When provided, deletes the requested file on the cloud service
              as well.

usage: dm_delete [-h] --key {} [--remote]
```
