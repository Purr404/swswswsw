FROM python:3.11-slim

WORKDIR /app

# CLEAN Python environment
RUN apt-get update && apt-get clean
RUN python -m pip install --upgrade pip
RUN pip cache purge

# Remove any existing discord.py
RUN pip uninstall -y discord discord.py py-cord || true

# Install ONLY discord.py v2
RUN pip install --no-cache-dir discord.py==2.3.2

# Verify installation
RUN python -c "import discord; print(f'INSTALLED: discord.py {discord.__version__}'); print(f'Has Bot attr: {hasattr(discord, \"Bot\")}')"

COPY bot.py .

CMD ["python", "bot.py"]