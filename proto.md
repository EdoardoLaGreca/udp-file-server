# Protocol

## Commands

Available commands:

 - `list` - list files
 - `get` - get file
 - `put` - put file

### `list` command

**Request** packet syntax:

```
list
```

where `DIR` is the desired directory path.

**Response** packet syntax:

```
FILENAME1
FILENAME2
FILENAME3
[...]
```

where:

 - `FILENAME1`, `FILENAME2`, `FILENAME3` are file names.

### `get` command

**Request** packet syntax:

```
get NAME
```

where:

 - `NAME` is the desired file name.

**Response** packet syntax:

```
FILE_CONTENT
```

where:

 - `FILE_CONTENT` is the content of the requested file.

### `put` command

**Request** packet syntax:

```
put NAME CONTENT
```

where:

 - `NAME` is the name of the file
 - `CONTENT` is the file content encoded using base64

**Response** packet syntax:

```
ok
```

## Error response

If any command fails, the server can send back an error message using the
following syntax:

```
error ERROR_MSG
```

where:

 - `ERROR_MSG` is the error message.
