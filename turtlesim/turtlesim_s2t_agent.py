import logging
import signal
import time
import rclpy

from rai_s2s.asr import  SpeechRecognitionAgent

# Set up basic logging to see what the agent is doing
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # optionally add additional models to decide when to record data for transcription
    # agent.add_detection_model(oww, pipeline="record")

    rclpy.init()

    agent = SpeechRecognitionAgent.from_config("config.toml")
    agent.run()

    def cleanup(signum, frame):
        agent.stop()
        rclpy.shutdown()
        exit(0)

    signal.signal(signal.SIGINT, cleanup)

    while True:
        time.sleep(1)
