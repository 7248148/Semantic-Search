# API

![api](../images/api.png#only-light)
![api](../images/api-dark.png#only-dark)

txtai has a full-featured API that can optionally be enabled for any txtai process. All functionality found in txtai can be accessed via the API. The following is an example configuration and startup script for the API.

Note that this configuration file enables all functionality. It is suggested that separate processes are used for each instance of a txtai component. Components can be joined together with workflows.

```yaml
# Index file path
path: /tmp/index

# Allow indexing of documents
writable: True

# Enbeddings index
embeddings:
  path: sentence-transformers/nli-mpnet-base-v2

# Extractive QA
extractor:
  path: distilbert-base-cased-distilled-squad

# Zero-shot labeling
labels:

# Similarity
similarity:

# Text segmentation
segmentation:
    sentences: true

# Text summarization
summary:

# Text extraction
textractor:
    paragraphs: true
    minlength: 100
    join: true

# Transcribe audio to text
transcription:

# Translate text between languages
translation:

# Workflow definitions
workflow:
    sumfrench:
        tasks:
            - action: textractor
              task: storage
              ids: false
            - action: summary
            - action: translation
              args: ["fr"]
    sumspanish:
        tasks:
            - action: textractor
              task: url
            - action: summary
            - action: translation
              args: ["es"]
```

Assuming this YAML content is stored in a file named index.yml, the following command starts the API process.

```
CONFIG=index.yml uvicorn "txtai.api:app"
```

uvicorn is a full-featured production ready server with support for SSL and more. See the [uvicorn deployment guide](https://www.uvicorn.org/deployment/) for details.

## Differences between Python and API

The txtai API provides all the major functionality found in this project. But there are differences due to the nature of JSON and differences across the supported programming languages. For example, any Python callable method is available at a named endpoint (i.e. instead of summary() the method call would be summary.summary()).
Return types vary as tuples are returned as objects via the API.

## Supported language bindings

The following programming languages have txtai bindings:

- [JavaScript](https://github.com/neuml/txtai.js)
- [Java](https://github.com/neuml/txtai.java)
- [Rust](https://github.com/neuml/txtai.rs)
- [Go](https://github.com/neuml/txtai.go)

See each of the projects above for details on how to install and use. Please add an issue to request additional language bindings!
