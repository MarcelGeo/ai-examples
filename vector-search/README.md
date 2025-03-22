# Vector Search in Geopackage (SQLite3)

This example uses embedding to create similarity vectors in a Geopackage (SQLite) database.

To run this example, use the following steps:

* Download `data_initial.gpkg` from [Hugging Face](https://huggingface.co/datasets/marcelgeo/overture-addresses-sample).
* Rename the file to `data.gpkg`.
* Run `python embedding.py` to perform embedding.

For similarity search, run `python qgis_search.py`. This script performs a similarity search over the data in the `embeddings` table and stores the scores in a QGIS layer.

For visualization of the results, open the `project.qgz` QGIS project.

## Configuration

To edit the query used for embedding, update the `embedding_query.py` QUERY variable. You can also edit the `.env` variables to run this example with a custom database and table.
