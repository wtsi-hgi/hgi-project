Development
-----------

To develop and test within the docker container (sorting out
prerequisities using the Dockerfile), you could run a command like:

```sh
docker build -t local/hgi-project . && \
docker run -v ~/.hgi-project:/etc/hgi-project.cfg \
           -v ~/secret.key:/etc/hgi-project.key \
           local/hgi-project \
           python hgip/api.py
```

This command bind-mounts the `~/.hgi-project` configuration file and
`~/secret.key` file from your machine into the Docker container as
`/etc/hgi-project.cfg` and `/etc/hgi-project.key`, respectively.
