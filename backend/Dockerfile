FROM python:3.12
WORKDIR /app
COPY requirements/requirements.dev.txt /app/requirements/requirements.dev.txt
COPY requirements/requirements.lint.txt /app/requirements/requirements.lint.txt
RUN pip install -r /app/requirements/requirements.dev.txt --no-cache-dir
COPY . /app/
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]