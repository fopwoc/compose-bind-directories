# Compose Bind Directories

[![CI](https://github.com/fopwoc/compose-bind-directories/actions/workflows/ci.yml/badge.svg)](https://github.com/fopwoc/compose-bind-directories/actions/workflows/ci.yml)
[![Ansible Galaxy](https://img.shields.io/badge/Ansible%20Galaxy-role-EE0000?logo=ansible&logoColor=white)](https://galaxy.ansible.com/ui/standalone/roles/fopwoc/compose_bind_directories/)

An Ansible role that renders a local Docker Compose YAML or Jinja2 file, finds
absolute bind-mount sources under configured roots, and creates missing
directories with explicit UID/GID ownership before containers start.

Docker otherwise creates missing bind sources as `root:root`, which can prevent
containers running as non-root users from starting or writing data.

> [!NOTE]
> This project contains AI-generated code. See [AI_USAGE.md](AI_USAGE.md) for details.

## Requirements

Controller:

- Ansible Core 2.16 or newer
- A Unix-like operating system

Remote host:

- Python supported by Ansible
- Permission to create bind directories with the requested ownership
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
        compose_bind_directories_allowed_roots:
          - /mnt/fast
          - /mnt/bulk
          - /mnt/data
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

Excluded sources are removed before allowed-root and filesystem checks. Use
exclusions for known file binds or paths managed elsewhere:

```yaml
compose_bind_directories_excluded_sources:
  - /etc/localtime
  - /srv/my-app/config.yaml
```

Compose environment interpolation cannot always distinguish a bind source from
a named volume before Compose runs. Use Jinja2 variables for dynamic source
paths that this role must prepare.

The default behavior matches `mkdir -p` ownership semantics:

- Missing directory sources are created with the requested UID, GID, and mode.
- Existing directories retain their ownership and mode.
- Existing regular files are reported and left unchanged.
- Existing symlinks are rejected.
- Sources outside the configured allowed roots are rejected.
- Directory contents are never traversed or changed recursively.

Permit known symlink sources explicitly; permitted links are reported and left
unchanged:

```yaml
compose_bind_directories_allow_symlinks: true
```

To reconcile the ownership and mode of existing directories themselves, opt in
explicitly. This still does not recurse into their contents:

```yaml
compose_bind_directories_reconcile_existing: true
```

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `compose_bind_directories_compose_file` | required | Local Compose YAML or Jinja2 file; relative paths use `playbook_dir`. |
| `compose_bind_directories_uid` | required | Numeric UID assigned to discovered directories. |
| `compose_bind_directories_gid` | required | Numeric GID assigned to discovered directories. |
| `compose_bind_directories_mode` | `0755` | Permissions assigned to discovered directories. |
| `compose_bind_directories_excluded_sources` | `[]` | Absolute bind sources the role must not manage. |
| `compose_bind_directories_allowed_roots` | `/mnt/fast`, `/mnt/bulk`, `/mnt/data` | Absolute roots under which bind directories may be managed. `/` is not permitted. |
| `compose_bind_directories_allow_symlinks` | `false` | Permit existing symlink sources without changing them. |
| `compose_bind_directories_reconcile_existing` | `false` | Apply requested ownership and mode to existing directories without recursing. |

## Development

Install Ansible Core and `ansible-lint`, then run:

```shell
scripts/check.sh
```

## Related project

[Just Deploy](https://github.com/fopwoc/just-deploy) transactionally deploys
ordinary Docker Compose project directories with rollback.
