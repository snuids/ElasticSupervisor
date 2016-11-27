FROM python
COPY . /bin
RUN ls -l

CMD ["python", "./ELKSupervisor.py"]

