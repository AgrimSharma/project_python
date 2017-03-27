import slumber

import logging

logger = logging.getLogger(__name__)

def post(token, source, from_address, subject, content, from_name, project, link):
    api = slumber.API("https://api.flowdock.com/v1/messages/", append_slash=False)   
    data = {
        "source": source,
        "from_address": from_address,
        "subject": subject,
        "content": content,
        "from_name": from_name,
        "project": project,
        "link": link
        }
    logger.debug("Data: %s" % data)
    api.team_inbox(token).post(data)