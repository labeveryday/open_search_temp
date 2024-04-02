import logging
import os
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth



# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Create a file handler
log_file = 'app.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

try:
    OPENSEARCH_ENDPOINT = os.environ["opensearch_host"]
    VECTOR_INDEX_NAME = os.environ["vector_index_name"]
    VECTOR_FIELD_NAME = os.environ["vector_field_name"]
    REGION = os.environ["aws_region"]
except Exception as e:
    logger.error(f"Unable to import environmental variable: {e}")

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
        try:
            res = ops_client.indices.create(index=VECTOR_INDEX_NAME, body=settings, ignore=[400])
            logger.info(f'Index creation response: {res}')
        except Exception as e:
            logger.error(f'Error creating index: {e}')


if __name__ == "__main__":
    create_index()