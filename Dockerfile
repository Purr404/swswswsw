FROM python:3.11-slim

WORKDIR /app

# Install discord.py v2
RUN pip install discord.py==2.3.2

COPY bot.py .

CMD ["python", "bot.py"]