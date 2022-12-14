FROM debian:latest
ARG LOG_arg
ARG api_name_arg
ARG alice_sentence_arg
ARG bob_sentence_arg
RUN apt-get update && apt-get install python3-pip -y && pip3 install requests
ADD test_authorization_alice.py /my_test_authorization/test_authorization_alice.py
ADD test_authorization_bob.py /my_test_authorization/test_authorization_bob.py
ADD test_pipeline.py /my_test_authorization/test_pipeline.py
RUN mkdir /my_log/
WORKDIR /my_test_authorization/
ENV LOG $LOG_arg
ENV api_name $api_name_arg
ENV alice_sentence_env $alice_sentence_arg
ENV bob_sentence_env $bob_sentence_arg
VOLUME my_log
CMD python3 test_pipeline.py
