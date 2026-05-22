# LangGraph Workflow Design

The current code keeps each agent as a normal Python service so it is easier to test and debug first. The intended LangGraph topology is below.

```text
upload_router
  -> enqueue_processing_job
  -> paddleocr_parser_agent
  -> chunking_agent
  -> rule_extraction_agent
  -> embedding_index_agent
  -> graph_builder_agent
  -> status_update_agent
```

Query path:

```text
query_router
  -> vector_retrieval_agent
  -> graph_expansion_agent
  -> citation_agent
  -> answer_generation_agent
  -> validation_agent
```

Implementation rule: keep each node small and commit each node separately.
