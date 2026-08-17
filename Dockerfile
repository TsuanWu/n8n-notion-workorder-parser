# MarkItDown is installed in a separate Alpine stage, then copied into n8n.
# This avoids relying on a package manager being present in the hardened n8n image.
FROM python:3.12-alpine3.22 AS markitdown

RUN python -m venv /opt/markitdown \
    && /opt/markitdown/bin/pip install --no-cache-dir "markitdown[pdf]"

# Reuse the Docker Hub image already used by the development workstation.
FROM n8nio/n8n:2.29.8

USER root
COPY --from=markitdown /usr/local /usr/local
COPY --from=markitdown /opt/markitdown /opt/markitdown
# Python's ctypes module in the builder depends on this Alpine runtime library.
COPY --from=markitdown /usr/lib/libffi.so.8 /usr/lib/libffi.so.8
ENV PATH="/opt/markitdown/bin:${PATH}"
# Temporary dispatch PDFs are written here by n8n before MarkItDown reads them.
# Keep this directory owned by the unprivileged n8n user.
RUN chmod 1777 /tmp \
    && mkdir -p /tmp/dispatch \
    && chown node:node /tmp/dispatch
USER node
