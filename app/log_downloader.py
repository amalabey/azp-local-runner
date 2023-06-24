import time

LOG_POLL_DELAY = 1


class LogDownloader:
    def __init__(self, piplines_client, pipeline_id, run_id):
        self.pipelines_client = piplines_client
        self.pipeline_id = pipeline_id
        self.run_id = run_id

    def start(self):
        self._poll_logs()

    def on_receive_log(self, log_lines):
        pass

    def _poll_logs(self):
        logs = dict()
        while True:
            logs_response = self.pipelines_client.get_logs(self.pipeline_id,
                                                           self.run_id)
            for log in logs_response["logs"]:
                log_id = log["id"]
                log_line_count = log["lineCount"] if "lineCount" in log else 0
                log_url = log["url"]
                previous_line_count = logs[log_id] if log_id in logs else 0
                if log_line_count > previous_line_count:
                    self._write_log_data(log_url, previous_line_count)
                    logs[log_id] = log_line_count

            # check pipeline status
            state, result = self.pipelines_client.get_run_state(self.pipeline_id,
                                                                self.run_id)
            if state == "completed":
                print(f"Pipeline completed: {result}")
                break
            time.sleep(LOG_POLL_DELAY)

    def _write_log_data(self, url, downloaded_line_count):
        log_contents = self.pipelines_client.get_log_content(url)
        new_contents = self._get_text_after_line(log_contents,
                                                 downloaded_line_count)
        self.on_receive_log(new_contents)

    def _get_text_after_line(self, text, line_number):
        lines = text.splitlines()
        if line_number >= len(lines):
            return ''  # Line number exceeds the total number of lines
        # Retrieve text after the specified line number
        text_after_line = '\n'.join(lines[line_number:])
        return text_after_line
