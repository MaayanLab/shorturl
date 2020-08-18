# Shorturl

URL shortener based on AWS DynamoDB. DynamoDB is a serverless key-value storage system. It can store JSON objects and identify them with up to two fields within the JSON.

The API exposes two API endpoints to register and redirct URLS. If a URL is sent to the API to be shortend it will produce a hash and save the original URL with the hash key in DynamoDB. If a client navigates to the shorturl endpoint with the hask key as the appendix he will be redirected to the correct URL.

Example:
'''
https://maayanlab.cloud/turl/2f59e093

Directs to:
https://maayanlab.cloud/Enrichr/enrich?dataset=7a8043c6bbb70d2f3bc871687047cdc8
'''