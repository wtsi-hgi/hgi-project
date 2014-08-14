Development
-----------

To develop and test within the docker container (sorting out prerequisities using the Dockerfile), you could run a command like:

```
docker build -t local/hgi-project . && docker run -v ~/.hgi-project:/etc/hgi-project.cfg local/hgi-project python hgip/api.py
```

This command bind-mounts the ~/.hgi-project configuration file from your machine into the Docker container as /etc/hgi-project.cfg

