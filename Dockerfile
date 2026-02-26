# Use a slim Python base image
FROM python:3.12-slim

# Upgrade pip to the latest version
RUN python -m pip install --upgrade pip

# System deps (no Google Chrome)
# Notes:
# - matplotlib works headless with Agg (no GUI libs needed)
# - TeX stack included for PDF compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    texlive-xetex texlive-latex-recommended texlive-latex-extra \
    texlive-bibtex-extra texlive-pictures texlive-fonts-recommended \
    texlive-fonts-extra texlive-lang-portuguese \
    texlive-plain-generic \
    latexmk biber \
    && rm -rf /var/lib/apt/lists/*

# Python runtime behavior
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Create the required folder structure
RUN mkdir -p /app/tex_files/figs \
             /app/tex_files/reports \
             /app/tex_files/tables \
             /app/tex_files/templates \
             /app/tex_files/reports/figs \
             /app/tex_files/reports/tables

# Expose Streamlit port
EXPOSE 8080

# Run Streamlit in headless mode
CMD ["streamlit","run","main.py","--server.port=8080","--server.address=0.0.0.0","--server.enableCORS=false","--server.headless=true"]
