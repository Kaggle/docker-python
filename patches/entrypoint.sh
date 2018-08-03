#!/usr/bin/env bash

# This shell script is executed as an entrypoint file for the Kernels docker image.
# It sets up the execution environment before starting the Jypyter Notebook Server.
# Refer to https://docs.docker.com/engine/reference/builder/#entrypoint for details.

# This script sets up pip to enable a user to install and use python modules via
# pip intall. $KAGGLE_WORKING_DIR should be available for it to work.
if [[ ! -z "${KAGGLE_WORKING_DIR}" ]]; then
    PIP_INSTALL_PREFIX_DIR="${KAGGLE_WORKING_DIR}/pip"
    PIP_INSTALLED_MODULE_DIR="${PIP_INSTALL_PREFIX_DIR}/pip_installed"
    PIP_CONFIG_FILE_PATH="${KAGGLE_WORKING_DIR}/config/pip/pip.conf"

    # Create a directory for pip to install modules.
    mkdir -p ${PIP_INSTALL_PREFIX_DIR}

    # Create pip config file to use the prefix directory created above for
    # installation. Also, ignore-installed is set to true to prevent pip
    # from trying to remove existing modules from the read-only filesystem.
    mkdir -p `dirname ${PIP_CONFIG_FILE_PATH}`
    echo -e "[install]\nprefix=${PIP_INSTALL_PREFIX_DIR}\nignore-installed=true" > ${PIP_CONFIG_FILE_PATH}
    # Instruct pip to use this config file.
    export PIP_CONFIG_FILE=${PIP_CONFIG_FILE_PATH}

    # Set up PYTHONPATH correctly to include the user-installed library.
    # Note that the pip prefix directory overrides the system default to enable
    # a user to use his/her installed one.
    # TODO(dsjang): Currently "lib/python3.6/site-packages" is hard-coded
    # throughout Dockerfile. Parameterize it to avoid a version mismatch.
    # TODO(dsjang): This is a hack to sidestep a problem of Python ignoring modules
    # in .../site-packages other than the system-wide and user-specific site packages.
    mkdir -p "${PIP_INSTALL_PREFIX_DIR}/lib/python3.6/site-packages"
    ln -s "${PIP_INSTALL_PREFIX_DIR}/lib/python3.6/site-packages" ${PIP_INSTALLED_MODULE_DIR}
    export PYTHONPATH=${PIP_INSTALLED_MODULE_DIR}:${PYTHONPATH}

    # Create a symbolic link to site-packages.
    # can't override conda installed package.

    # Include pip-installed binaries in PATH.
    export PATH=${PATH}:${PIP_INSTALL_PREFIX_DIR}/bin
fi

# Execute the command provided from "docker run" in the current process.
exec "$@"