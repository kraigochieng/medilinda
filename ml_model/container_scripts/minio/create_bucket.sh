sleep 5
mc alias set minioserver "http://minio:${MINIO_API_PORT}" "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"

mc mb "minioserver/${MINIO_BUCKET_NAME}"
mc mb "minioserver/${MINIO_BUCKET_NAME}" || echo "Bucket already exists"

#Set public policy so MLflow can access it
echo "Granting public access to the bucket..."
mc anonymous set public "minioserver/${MINIO_BUCKET_NAME}" || echo "Failed to set public access."

mc ls minioserver