from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.conf import settings

class QuotaUploadHandler(FileUploadHandler):
    """
    An upload handler which terminates the connection once more than
    QUOTA bytes have been uploaded to the server.  This tries to manage
    any DoS where a huge file is uploaded to the server.
    The QUOTA needs to be large enough so that the error is not presented
    unless unreasonably large files are uploaded, but small enough that
    large files don't stall the server.
    """

    QUOTA = 50 * 1024 * 1024

    def __init__(self, request=None):
        super(QuotaUploadHandler, self).__init__(request)
        self.total_upload = 0

    def receive_data_chunk(self, raw_data, start):
        self.total_upload += len(raw_data)
        if self.total_upload >= self.QUOTA:
            raise StopUpload(connection_reset=True)
        return raw_data

    def file_complete(self, file_size):
        return None

