FROM python:3.8

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN sed -i 's!http://localhost:5000!https://api.dtpoc.knowit.no!g' ssb_wms_getcapabilities.xml
RUN pyproj sync --source-id no_kv
EXPOSE 5000

CMD ["python", "flask_server.py"]