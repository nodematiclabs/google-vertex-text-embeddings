import kfp
import kfp.dsl as dsl

from kfp import compiler
from kfp.dsl import Dataset, Input

from typing import List

@dsl.component(
    base_image="python:3.11",
    packages_to_install=["google-cloud-aiplatform", "appengine-python-standard"],
)
def generate_embeddings(blog_post: Input[Dataset]) -> List[float]:
    import json
    import os
    from vertexai.preview.language_models import TextEmbeddingModel

    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

    with open(blog_post.metadata["local_gcs_uri"], 'r') as f:
        text = f.read()
        embeddings = model.get_embeddings([text])
        return embeddings[0].values

@dsl.component(
    base_image="python:3.11",
    packages_to_install=["google-cloud-aiplatform", "appengine-python-standard"],
)
def generate_recommendations(embedding: List[float]) -> str:
    import json

    from google.cloud import aiplatform
    from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import Namespace

    similarity_engine = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name = "REPLACE_ME"
    )

    responses = similarity_engine.match(
        deployed_index_id="similarity_engine",
        queries=[embedding],
        num_neighbors=4
    )

    return json.dumps([{"id": neighbor.id, "distance": neighbor.distance} for neighbor in responses[0]])

@dsl.pipeline(name="similarity-engine-blog-post-recommendations")
def blog_post_recommendations(gcs_bucket: str, blog_post_filepath: str):
    blog_post = dsl.importer(
        artifact_uri=f'gs://{gcs_bucket}/{blog_post_filepath}',
        artifact_class=Dataset,
        reimport=False,
        metadata={
            "local_gcs_uri": f'/gcs/{gcs_bucket}/{blog_post_filepath}'
        }
    )
    generate_embeddings_task = generate_embeddings(blog_post=blog_post.output)
    generate_recommendations(embedding=generate_embeddings_task.output)

compiler.Compiler().compile(blog_post_recommendations, "pipeline.yaml")