# Use a slim Python base image
FROM python:3.12-slim

# System deps (TeX stack for later PDF compilation)  — comments in English only
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential \
#    texlive-xetex texlive-latex-recommended texlive-latex-extra \
#    texlive-bibtex-extra texlive-pictures texlive-fonts-recommended \
#    texlive-fonts-extra texlive-lang-portuguese \
#    latexmk biber \
#    && rm -rf /var/lib/apt/lists/*

# Python runtime behavior
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Python deps (use cache effectively)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose Streamlit port
EXPOSE 8080

# Run Streamlit in headless mode, reachable from outside the container
CMD ["streamlit","run","main.py","--server.port=8080","--server.address=0.0.0.0","--server.enableCORS=false","--server.headless=true"]

