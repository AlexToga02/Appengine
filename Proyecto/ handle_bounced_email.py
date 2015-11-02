import logging
import webapp
from google.appengine.ext.webapp.mail_handlers import BounceNotification
from google.appengine.ext.webapp.mail_handlers import BounceNotificationHandler

class LogBounceHandler(BounceNotificationHandler):
  def receive(self, bounce_message):
    logging.info('Received bounce post ... [%s]', str(self.request))
    logging.info('Bounce original: %s' + str(bounce_message.original))
    logging.info('Bounce notification: %s' + str(bounce_message.notification))


app = webapp2.WSGIApplication(["/_ah/bounce",LogBounceHandler],debug=True, config=config)
