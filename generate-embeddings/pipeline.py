import kfp
import kfp.dsl as dsl

from kfp import compiler
from kfp.dsl import Dataset, Input, Output

from typing import List

@dsl.component(
    base_image="python:3.11",
    packages_to_install=["google-cloud-aiplatform", "appengine-python-standard"],
)
def generate_embeddings(markdown_gcs_dir: str):
    import json
    import os
    from vertexai.preview.language_models import TextEmbeddingModel

    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

    local_dir = markdown_gcs_dir.replace("gs://", "/gcs/") + "/content/"
    # Loop over files in the GCS directory
    data = []
    for filename in os.listdir(local_dir):
        if filename.endswith(".md"):
            with open(os.path.join(local_dir, filename), 'r') as f:
                text = f.read()
                embeddings = model.get_embeddings([text])
                for embedding in embeddings:
                    data.append(
                        json.dumps(
                            {
                                "id": filename.replace(".md", ""),
                                "embedding": embedding.values,
                                "restricts": [
                                    {"namespace": "content", "allow": ["blog"]}
                                ]
                            }
                        )
                    )

    with open(markdown_gcs_dir.replace('gs://', '/gcs/') + "engine/data.json", 'w') as f:
        f.write("\n".join(data))


@dsl.pipeline(name="similarity-engine-blog-posts")
def transcript_extraction():
    generate_embeddings(markdown_gcs_dir="gs://REPLACE_ME/blog-posts/")

compiler.Compiler().compile(transcript_extraction, "pipeline.yaml")