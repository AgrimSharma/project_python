from storages.backends.s3 import S3Storage
import mimetypes
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SimpleNameS3Storage(S3Storage):
    def _save(self, name, content):
        name = self._clean_name(name)
        if hasattr(content, "open"):
            content.open()
        if hasattr(content, 'chunks'):
            content_str = ''.join(chunk for chunk in content.chunks())
        else:
            content_str = content.read()
        self._put_file(name, content_str)
        return name

    def _put_file(self, name, content):
        if self.encrypt:
            # Create a key object
            key = self.crypto_key()

            # Read in a public key
            fd = open(settings.CRYPTO_KEYS_PUBLIC, "rb")
            public_key = fd.read()
            fd.close()

            # import this public key
            key.importKey(public_key)

            # Now encrypt some text against this public key
            content = key.encString(content)
        content_type = mimetypes.guess_type(name)[0] or "application/x-octet-stream"

        if self.gzip and content_type in self.gzip_content_types:
            logger.debug(self.gzip)
            content = self._compress_string(content)
            self.headers.update({'Content-Encoding': 'gzip'})
        self.headers.update({
            'x-amz-acl': self.acl,
            'Content-Type': content_type,
            'Content-Length' : str(len(content)),
            'Content-Disposition': "attachment; filename=\"%s\"" % name.split("/")[-1].encode("utf-8")
        })
        response = self.connection.put(self.bucket, name, content, self.headers)
        if response.http_response.status not in (200, 206):
            raise IOError("S3StorageError: %s" % response.message)
