FROM mcr.microsoft.com/devcontainers/go:1-1.24-bookworm

COPY hugo /usr/local/bin/hugo

# The upstream Go image still includes Yarn's old APT source. Its signing key
# has been retired, and this container does not need Yarn.
RUN chmod +x /usr/local/bin/hugo \
    && rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        fd-find \
        git \
        python3 \
        python3-pip \
        python3-venv \
        ripgrep \
        unzip \
    && curl -fsSL "https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz" \
        | tar -xz -C /opt \
    && ln -s /usr/bin/fdfind /usr/local/bin/fd \
    && curl -fsSL https://opencode.ai/install -o /tmp/opencode-install \
    && OPENCODE_INSTALL_DIR=/usr/local/bin bash /tmp/opencode-install --no-modify-path \
    && rm /tmp/opencode-install \
    && GOTOOLCHAIN=auto go install -tags extended github.com/gohugoio/hugo@latest \
    && mkdir -p /usr/local/libexec \
    && mv /go/bin/hugo /usr/local/libexec/hugo \
    && ln -s /usr/local/bin/hugo /go/bin/hugo \
    && GOTOOLCHAIN=auto go install github.com/jesseduffield/lazygit@latest \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/local/bin:/opt/nvim-linux-x86_64/bin:/go/bin:/home/vscode/.venv/bin:${PATH}"
