import threading
import time

LOG_POLL_DELAY = 1


class LogDownloader:
    def __init__(self, piplines_client, pipeline_id, run_id):
        self.pipelines_client = piplines_client
        self.pipeline_id = pipeline_id
        self.run_id = run_id

    def start(self, stream):
        stream_writer = StreamWriter(stream)
        thread = threading.Thread(target=self._poll_logs, args=(stream_writer))
        thread.start()

    def _poll_logs(self, stream_writer):
        logs = dict()
        while True:
            logs_response = self.pipelines_client.get_logs(self.pipeline_id,
                                                           self.run_id)
            for log in logs_response["logs"]:
                log_id = log["id"]
                log_line_count = log["lineCount"]
                log_url = log["url"]
                previous_line_count, _ = logs[log_id]
                if log_line_count > previous_line_count:
                    self._write_log_data(log_url, previous_line_count,
                                         stream_writer)
                logs[log_id] = log_line_count

            # check pipeline status
            state, result = self.pipelines_client.get_run_state(self.pipeline_id,
                                                                self.run_id)
            if state == "completed":
                print(f"Pipeline completed: {result}")
                break
            time.sleep(LOG_POLL_DELAY)

    def _write_log_data(self, url, downloaded_line_count, stream_writer):
        log_contents = self.pipelines_client.get_log_content(url)
        new_contents = self._get_text_after_line(log_contents,
                                                 downloaded_line_count)
        stream_writer.write_text(new_contents)

    def _get_text_after_line(text, line_number):
        lines = text.splitlines()
        if line_number >= len(lines):
            return ''  # Line number exceeds the total number of lines
        # Retrieve text after the specified line number
        text_after_line = '\n'.join(lines[line_number:])
        return text_after_line


class StreamWriter:
    def __init__(self, stream):
        self.stream = stream
        self.lock = threading.Lock()

    def write_text(self, message):
        with self.lock:
            self.stream.write(message)
            self.stream.flush()
