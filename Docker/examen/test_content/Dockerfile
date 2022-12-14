FROM debian:latest
ARG LOG_arg
ARG api_name_arg
ARG pos_sentence_arg
ARG neg_sentence_arg
RUN apt-get update && apt-get install python3-pip -y && pip3 install requests
ADD test_content_alice_v1.py /my_test_content/test_content_alice_v1.py
ADD test_content_alice_v2.py /my_test_content/test_content_alice_v2.py
ADD test_pipeline.py /my_test_content/test_pipeline.py
RUN mkdir /my_log/
WORKDIR /my_test_content/
ENV LOG $LOG_arg
ENV api_name $api_name_arg
ENV pos_sentence_env $pos_sentence_arg
ENV neg_sentence_env $neg_sentence_arg
VOLUME my_log
CMD python3 test_pipeline.py
