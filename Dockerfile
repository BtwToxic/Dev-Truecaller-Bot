FROM python:3.10-slim

# env settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# workdir
WORKDIR /app

# install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy bot code
COPY . .

# start bot
CMD ["python", "bot.py"]
