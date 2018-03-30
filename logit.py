import logging

LOG_LEVEL_NUM = 100
logging.addLevelName(LOG_LEVEL_NUM, "LOGIT")


def logit(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(LOG_LEVEL_NUM):
        self._log(LOG_LEVEL_NUM, message, args, **kws)

logging.Logger.logit = logit