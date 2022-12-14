FROM debian:latest
ARG LOG_arg
ARG api_name_arg
RUN apt-get update && apt-get install python3-pip -y && pip3 install requests
ADD test_authentication_alice.py /my_test_authentication/test_authentication_alice.py
ADD test_authentication_bob.py /my_test_authentication/test_authentication_bob.py
ADD test_authentication_clementine.py /my_test_authentication/test_authentication_clementine.py
ADD test_pipeline.py /my_test_authentication/test_pipeline.py
RUN mkdir /my_log/
WORKDIR /my_test_authentication/
ENV LOG $LOG_arg
ENV api_name $api_name_arg
VOLUME my_log
CMD python3 test_pipeline.py
