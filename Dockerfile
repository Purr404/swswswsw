FROM python:3.11-slim

WORKDIR /app

# Install py-cord (has discord.Bot and modals)
RUN pip install --no-cache-dir "py-cord==2.5.0"

COPY bot.py .

CMD ["python", "bot.py"]