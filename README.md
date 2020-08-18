# Shorturl

URL shortener based on AWS DynamoDB. DynamoDB is a serverless key-value storage system. It can store JSON objects and identify them with up to two fields within the JSON.

The API exposes two API endpoints to register and redirct URLS. If a URL is sent to the API to be shortend it will produce a hash and save the original URL with the hash key in DynamoDB. If a client navigates to the shorturl endpoint with the hask key as the appendix he will be redirected to the correct URL.

Example:
```
https://maayanlab.cloud/turl/2f59e093

Directs to:
https://maayanlab.cloud/Enrichr/enrich?dataset=7a8043c6bbb70d2f3bc871687047cdc8
```

## Registering new shortened URLs

To shorten a new URL the user needs to be in possession of an API key. This key is part of the POST request.

Example:
``` python
import requests

payload = {
        'url': 'https://amp.pharm.mssm.edu/geneshot/index.html?searchin=Wound healing&searchnot=&rif=autorif',
        'apikey': 'secretkey'    
    }

response = requests.post('https://maayanlab.cloud/turl/api', json=payload)
print("Status code: ", response.status_code)
print("Printing Entire Post Request")
print(response.json())
```

## Configuring AWS

### Create Table in DynamoDB

Go to DynamoDB and create table. Choose a table name, this name will have to be specified as an environmental variable `DYNAMODB_TABLE` when the webserver is deployed. Set the primary key to `url`. That's it.

### User

Create a new role for DynamoDB user with programmatic access in IAM. Click Next: Permissions and select `Attach existing policies directly`. Select `Create Policy` and paste:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "dynamodb:*"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        }
    ]
}
```

It is possible to set finer grain rights. Please refer to:
https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_dynamodb_specific-table.html

Write down the AWS id and AWS key. They will be needed as environmental variables (`AWS_ID`, `AWS_KEY`) when deploying the server. Avoid adding them to the code.

## Deploying the webserver

The webserver is available as a Docker container at maayanlab/shorturl. Depending where is will be accessible adjust the `DOMAIN` and `ENDPOINT` accortingly. In this example the webserver is exposed at `https://maayanlab.cloud/turl`. 

The server expects the following environmental variables:
`AWS_ID` = AWS user id <br>
`AWS_KEY` = AWS user key <br>
`DOMAIN` = "https://maayanlab.cloud" <br>
`ENDPOINT` = "turl" <br>
`API_KEY` = "apipassword" <br>
`DYNAMODB_TABLE` = "shorturl" <br>

## Deploy docker container

Run prebuilt docker container on local host. Modify variables as needed.

```
sudo docker run \ 
    -e AWS_ID='XXXXXX' \
    -e AWS_KEY='YYYYYY' \
    -e DOMAIN='https://maayanlab.cloud' \
    -e ENDPOINT='turl' \
    -e API_KEY='secretkey' \
    -p 3000:3000 \
    -d --name="turl" maayanlab/shorturl 
```

