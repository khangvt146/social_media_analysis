from pyspark.sql.streaming import StreamingQueryListener

from utils.logger import Logger


class KafkaToGcsQueryListener(StreamingQueryListener):
    def __init__(self, logger: Logger):
        self.logger = logger
        super().__init__()

    def onQueryStarted(self, event):
        # Log when a query starts
        self.logger.info(
            f"Query started: 'id'={event.id}, 'runId'={event.runId}, 'name'={event.name}"
        )

    def onQueryProgress(self, event):
        # Log the progress of each batch
        progress = event.progress
        self.logger.info(
            f"Query progress: 'id'={progress.id}, 'num_rows'={progress.numInputRows}, processed_rows_per_second={progress.processedRowsPerSecond}"
        )
        self.logger.info(
            f"Query progress: 'id'={progress.id}, duration per batch (ms): {progress.durationMs}"
        )

    def onQueryTerminated(self, event):
        # Log when the query terminates
        self.logger.info(f"Query terminated: id={event.id}, runId={event.runId}")
