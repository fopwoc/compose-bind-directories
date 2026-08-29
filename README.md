# Compose Bind Directories

[![CI](https://github.com/fopwoc/compose-bind-directories/actions/workflows/ci.yml/badge.svg)](https://github.com/fopwoc/compose-bind-directories/actions/workflows/ci.yml)
[![Ansible Galaxy](https://img.shields.io/badge/Ansible%20Galaxy-role-EE0000?logo=ansible&logoColor=white)](https://galaxy.ansible.com/ui/standalone/roles/fopwoc/compose_bind_directories/)

An Ansible role that renders a local Docker Compose YAML or Jinja2 file, finds
absolute bind-mount sources, and creates those directories with explicit
UID/GID ownership before containers start.

Docker otherwise creates missing bind sources as `root:root`, which can prevent
containers running as non-root users from starting or writing data.

## Requirements

Controller:

- Ansible Core 2.16 or newer
- A Unix-like operating system

Remote host:

- Python supported by Ansible
- Permission to create and change ownership of the bind directories
- A Unix-like operating system

Docker is not required while this role runs.

## Installation

```shell
ansible-galaxy role install fopwoc.compose_bind_directories
```

Or add the role to `requirements.yml`:

```yaml
---
roles:
  - name: fopwoc.compose_bind_directories
```

## Usage

The Compose file is rendered on the controller with variables from the play
before its volumes are inspected:

```yaml
---
- name: Prepare application bind directories
  hosts: app
  gather_facts: false
  tasks:
    - name: Prepare Compose bind directories
      ansible.builtin.include_role:
        name: fopwoc.compose_bind_directories
        apply:
          become: true
      vars:
        compose_bind_directories_uid: 1000
        compose_bind_directories_gid: 1000
      loop:
        - "{{ playbook_dir }}/compose/app.yaml.j2"
      loop_control:
        loop_var: compose_bind_directories_compose_file
```

The loop is optional for one file; set
`compose_bind_directories_compose_file` directly in that case. UID and GID are
configured per role invocation, so separate tasks can use different ownership
policies.

Both short and long bind syntax are supported:

```yaml
services:
  app:
    volumes:
      - "{{ app_data_path }}:/var/lib/app"
      - type: bind
        source: "{{ app_cache_path }}"
        target: /var/cache/app
```

Named volumes, anonymous volumes, and non-bind long syntax are ignored. Only
absolute bind sources are created; relative sources belong to the Compose
project directory and are reported without being changed.

Every discovered absolute source is treated as a directory. Exclude file bind
sources and paths managed elsewhere:

```yaml
compose_bind_directories_excluded_sources:
  - /etc/localtime
  - /srv/my-app/config.yaml
```

Compose environment interpolation cannot always distinguish a bind source from
a named volume before Compose runs. Use Jinja2 variables for dynamic source
paths that this role must prepare.

Existing directories receive the requested ownership and mode without
recursively changing their contents.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `compose_bind_directories_compose_file` | required | Local Compose YAML or Jinja2 file; relative paths use `playbook_dir`. |
| `compose_bind_directories_uid` | required | Numeric UID assigned to discovered directories. |
| `compose_bind_directories_gid` | required | Numeric GID assigned to discovered directories. |
| `compose_bind_directories_mode` | `0755` | Permissions assigned to discovered directories. |
| `compose_bind_directories_excluded_sources` | `[]` | Absolute bind sources the role must not manage. |

## Development

Install Ansible Core and `ansible-lint`, then run:

```shell
scripts/check.sh
```

## Related project

[Just Deploy](https://github.com/fopwoc/just-deploy) transactionally deploys
ordinary Docker Compose project directories with rollback.
