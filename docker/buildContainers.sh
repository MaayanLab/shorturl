# get rid of old stuff
docker rmi -f $(docker images | grep "^<none>" | awk "{print $3}")
docker rm $(docker ps -q -f status=exited)

# build container
docker build -f DockerURL -t maayanlab/shorturl .
docker push maayanlab/shorturl

# launch locally
sudo docker run \ 
    -e AWS_ID='XXXXXX' \
    -e AWS_KEY='YYYYYY' \
    -e AWS_REGION='us-east-1' \
    -e DOMAIN='http://localhost:5000' \
    -e ENDPOINT='turl' \
    -e API_KEY='secretkey' \
    -p 5000:5000 \
    -d --name="turl" maayanlab/shorturl 
