# hgi-project

HGI Project tracking database with a hypermedia-driven RESTful
interface.

Also includes components for synchronising with other data sources
(e.g., LDAP).

## Development

To develop and test within the Docker container (sorting out
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

## License

Copyright (c) 2014, 2015 Genome Research Limited

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

---

The usage of a range of years within a copyright statement contained
within this distribution should be interpreted as being equivalent to a
list of years including the first and last year specified and all
consecutive years between them. For example, a copyright statement that
reads 'Copyright (c) 2005, 2007-2009, 2011-2012' should be interpreted
as being identical to a statement that reads 'Copyright (c) 2005, 2007,
2008, 2009, 2011, 2012' and a copyright statement that reads 'Copyright
(c) 2005-2012' should be interpreted as being identical to a statement
that reads 'Copyright (c) 2005, 2006, 2007, 2008, 2009, 2010, 2011,
2012'. 
