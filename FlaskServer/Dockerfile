FROM python

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN sed -i 's!http://localhost:5000!https://api.dtpoc.knowit.no!g' ssb_wms_getcapabilities.xml
EXPOSE 5000

CMD ["python", "flask_server.py"]