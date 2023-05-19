resource "google_compute_network" "similarity_engine" {
  name = "similarity-engine"
}

resource "google_compute_global_address" "private_ip_alloc" {
  name          = "private-ip-alloc"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.similarity_engine.id
}

resource "google_service_networking_connection" "default" {
  network                 = google_compute_network.similarity_engine.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}

resource "google_compute_network_peering_routes_config" "peering_routes" {
  peering = google_service_networking_connection.default.peering
  network = google_compute_network.similarity_engine.name

  import_custom_routes = true
  export_custom_routes = true
}

resource "google_vertex_ai_index" "blog_post_similarity" {
  region = "us-central1"
  display_name = "blog-post-similarity"
  metadata {
    contents_delta_uri = "gs://REPLACE_ME/blog-posts/engine/"
    config {
      dimensions = 768
      approximate_neighbors_count = 4
      distance_measure_type = "COSINE_DISTANCE"
      feature_norm_type = "UNIT_L2_NORM"
      algorithm_config {
        brute_force_config {}
      }
    }
  }
  index_update_method = "BATCH_UPDATE"
}