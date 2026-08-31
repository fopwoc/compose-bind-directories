#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: compose_bind_canonical_paths
short_description: Resolve paths through their nearest existing ancestors
description:
  - Finds the nearest existing ancestor of each absolute path.
  - Resolves that ancestor through symbolic links on the managed host.
  - Reattaches any non-existent path suffix without changing the filesystem.
options:
  paths:
    description: Absolute paths to resolve.
    type: list
    elements: path
    required: true
author:
  - Ilya Dobryakov
"""

EXAMPLES = r"""
---
- name: Resolve bind paths on the managed host
  compose_bind_canonical_paths:
    paths:
      - /mnt/data/app
"""

RETURN = r"""
paths:
  description: Resolution details in input order.
  returned: always
  type: list
  elements: dict
  contains:
    path:
      description: Normalized input path.
      type: str
    nearest_existing_ancestor:
      description: Nearest existing filesystem object in the input path.
      type: str
    canonical_nearest_existing_ancestor:
      description: Real path of the nearest existing ancestor.
      type: str
    canonical_path:
      description: Canonical ancestor with the non-existent suffix reattached.
      type: str
"""

import errno
import os

from ansible.module_utils.basic import AnsibleModule


def resolve_path(path):
    normalized_path = os.path.normpath(path)
    if not os.path.isabs(normalized_path):
        raise ValueError("path must be absolute: {0}".format(path))

    nearest_existing_ancestor = normalized_path
    missing_parts = []

    while True:
        try:
            os.lstat(nearest_existing_ancestor)
            break
        except OSError as error:
            if error.errno not in (errno.ENOENT, errno.ENOTDIR):
                raise

            parent = os.path.dirname(nearest_existing_ancestor)
            if parent == nearest_existing_ancestor:
                raise

            missing_parts.append(os.path.basename(nearest_existing_ancestor))
            nearest_existing_ancestor = parent

    canonical_ancestor = os.path.realpath(nearest_existing_ancestor)
    canonical_path = os.path.normpath(
        os.path.join(canonical_ancestor, *reversed(missing_parts))
    )

    return {
        "path": normalized_path,
        "nearest_existing_ancestor": nearest_existing_ancestor,
        "canonical_nearest_existing_ancestor": canonical_ancestor,
        "canonical_path": canonical_path,
    }


def main():
    module = AnsibleModule(
        argument_spec={
            "paths": {
                "type": "list",
                "elements": "path",
                "required": True,
            }
        },
        supports_check_mode=True,
    )

    try:
        resolved_paths = [resolve_path(path) for path in module.params["paths"]]
    except (OSError, ValueError) as error:
        module.fail_json(msg="Unable to resolve canonical path: {0}".format(error))

    module.exit_json(changed=False, paths=resolved_paths)


if __name__ == "__main__":
    main()
