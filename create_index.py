import boto3
import os
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth


OPENSEARCH_ENDPOINT = os.environ["opensearch_host"]
VECTOR_INDEX_NAME = os.environ["vector_index_name"]
VECTOR_FIELD_NAME = os.environ["vector_field_name"]
REGION = os.environ["aws_region"]

credentials = boto3.Session().get_credentials()
service = 'aoss'
auth = AWSV4SignerAuth(credentials, REGION, service)

# Connect to open search
ops_client = OpenSearch(
    hosts = [{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 20
)

# Create an opensearch index if it does not exist
def create_index():
    print(f'In create index')
    if not ops_client.indices.exists(index=VECTOR_INDEX_NAME):
    # Create indicies
        settings = {
            "settings": {
                "index": {
                    "knn": True,
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "text": {"type": "text"},
                    VECTOR_FIELD_NAME : {
                        "type": "knn_vector",
                        "dimension": 4096,
                    },
                }
            },
        }
        res = ops_client.indices.create(index=VECTOR_INDEX_NAME, body=settings, ignore=[400])
        print(res)


create_index()