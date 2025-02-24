# File: C:\cygwin64\home\student\Test_Strategies\MES\exit_manager.py
################################################################################

class ExitManager:
    def __init__(self):
        self.last_exit_signal = None

    def evaluate_exit(self, data_point: dict, indicators: dict, position: dict):
        """
        We no longer exit based on indicators.
        Always return None so that we rely solely on the stop-loss/take-profit logic.
        """
        return None
