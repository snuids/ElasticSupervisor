FROM python
COPY . /bin
ENV 
CMD ["python", "/bin/ELKSupervisor.py"]

