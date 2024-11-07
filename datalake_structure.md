```
gs://social_media_datalake/
├── reddit_data
|    |
|    ├── year=2024
|            └── month=01
|                └── day=01      
|                    ├── subreddit=technology
|                    │   ├── minibatch-00000.snappy.parquet
|                    │   └── minibatch-00001.snappy.parquet
|                    |
|                    ├── subreddit=science
|                    │   ├── minibatch-00000.snappy.parquet
|                    │   └── minibatch-00001.snappy.parquet
|                    |
|                    └── subreddit=futurology
|                        ├── minibatch-00000.snappy.parquet
|                        └── minibatch-00001.snappy.parquet
|
├── stack_exchange_data                  
|    |
|    ├── year=2024
|           └── month=01
|                ├──  day=01      
|                |    ├── exchange_page=stack_over_flow
|                |    │   ├── minibatch-00000.snappy.parquet
|                |    │   └── minibatch-00001.snappy.parquet
|                |    |
|                |    ├── exchange_page=askubuntu
|                |    │   ├── minibatch-00000.snappy.parquet
|                |    │   └── minibatch-00001.snappy.parquet
|                |    |
|                |    └── exchange_page=devops_stack_exchange
|                |        ├── minibatch-00000.snappy.parquet
|                |        └── minibatch-00001.snappy.parquet
|                |       
|                ├──  day=02
|                |    ├── ...
|
```

