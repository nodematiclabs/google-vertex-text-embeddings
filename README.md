
Create the endpoint:
```bash
gcloud ai index-endpoints create \
  --display-name="similarity-engine" \
  --network="projects/REPLACE_ME/global/networks/similarity-engine" \
  --region=us-central1
```

Delete the endpoint:
```bash
gcloud ai index-endpoints delete REPLACE_ME \
  --region=us-central1
```

Deploy to the endpoint:
```bash
gcloud ai index-endpoints deploy-index REPLACE_ME \
  --deployed-index-id="similarity_engine" \
  --display-name="similarity-engine" \
  --index="REPLACE_ME" \
  --region=us-central1
```

Generate recommendations:
```python
from google.cloud import aiplatform

job = aiplatform.PipelineJob(
    display_name="similarity-engine-blog-post-recommendations",
    template_path = "gs://REPLACE_ME/blog-posts/pipeline.yaml",
    pipeline_root = "gs://REPLACE_ME",
    parameter_values = {
        "gcs_bucket": "REPLACE_ME",
        "blog_post_filepath": "blog-posts/content/REPLACE_ME.md"
    },
    location = "us-central1",
)

job.submit(network="projects/REPLACE_ME/global/networks/similarity-engine")
```